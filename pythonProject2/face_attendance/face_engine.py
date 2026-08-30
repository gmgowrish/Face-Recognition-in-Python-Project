from pathlib import Path

import cv2
import numpy as np

from . import config


class FaceEngine:
    """Face detection, dataset capture, training and recognition.

    Kept free of any GUI dependency so it can be driven from the Qt UI or
    exercised directly in tests.
    """

    def __init__(self, faces_dir: Path | None = None, classifier_path: Path | None = None):
        self.faces_dir = Path(faces_dir or config.FACES_DIR)
        self.faces_dir.mkdir(parents=True, exist_ok=True)
        self.classifier_path = Path(classifier_path or config.CLASSIFIER_PATH)
        self.detector = self._load_cascade(config.BUNDLED_CASCADE_PATH, "haarcascade_frontalface_default.xml")
        self.eye_detector = self._load_cascade(config.BUNDLED_EYE_CASCADE_PATH, "haarcascade_eye.xml")

    @staticmethod
    def _load_cascade(bundled_path: Path, cv2_data_name: str) -> cv2.CascadeClassifier:
        cascade_path = str(bundled_path) if bundled_path.exists() else cv2.data.haarcascades + cv2_data_name
        detector = cv2.CascadeClassifier(cascade_path)
        if detector.empty():
            raise RuntimeError(f"Failed to load Haar cascade from {cascade_path}")
        return detector

    def detect_faces(self, frame_bgr: np.ndarray):
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        return gray, faces

    def largest_face(self, faces):
        if len(faces) == 0:
            return None
        return max(faces, key=lambda box: box[2] * box[3])

    def eyes_open(self, gray: np.ndarray, box) -> bool:
        """Best-effort liveness/quality gate, not real anti-spoofing.

        Haar eye detection reliably fails on closed eyes and on faces turned
        too far from the camera, which is what this actually checks. It is
        not a defense against a printed photo or a phone screen held up to
        the camera -- that needs texture/depth/motion analysis this
        Haar+LBPH pipeline doesn't do.
        """
        x, y, w, h = box
        # Eyes sit in the upper half of the face box; restricting the search
        # there cuts false positives from nostrils/mouth substantially.
        upper_half = gray[y : y + h // 2, x : x + w]
        eyes = self.eye_detector.detectMultiScale(upper_half, scaleFactor=1.1, minNeighbors=8, minSize=(20, 20))
        return len(eyes) >= config.MIN_OPEN_EYES

    def face_size_ok(self, box) -> bool:
        _, _, w, h = box
        return w >= config.MIN_FACE_SIZE and h >= config.MIN_FACE_SIZE

    def sharpness(self, gray: np.ndarray, box) -> float:
        """Laplacian variance of the face crop -- low means blurry/out of focus."""
        x, y, w, h = box
        crop = gray[y : y + h, x : x + w]
        return float(cv2.Laplacian(crop, cv2.CV_64F).var())

    def capture_quality(self, gray: np.ndarray, box) -> tuple[bool, str]:
        """Gate for auto-capturing a *good* sample, not just any detected face."""
        if not self.face_size_ok(box):
            return False, "Move closer to the camera"
        if not self.eyes_open(gray, box):
            return False, "Eyes closed or not clearly visible"
        if self.sharpness(gray, box) < config.MIN_SHARPNESS:
            return False, "Hold still (image is blurry)"
        return True, "Good"

    def _crop(self, gray: np.ndarray, box) -> np.ndarray:
        x, y, w, h = box
        face = cv2.resize(gray[y : y + h, x : x + w], config.FACE_SAMPLE_SIZE)
        # Normalizes lighting so LBPH distances are comparable across
        # different rooms/webcams instead of dominated by brightness.
        return cv2.equalizeHist(face)

    def save_sample(self, student_id: int, gray: np.ndarray, box, sample_index: int) -> Path:
        face = self._crop(gray, box)
        path = self.faces_dir / f"{student_id}.{sample_index}.jpg"
        cv2.imwrite(str(path), face)
        return path

    def sample_count(self, student_id: int) -> int:
        return len(list(self.faces_dir.glob(f"{student_id}.*.jpg")))

    def clear_samples(self, student_id: int | None = None) -> int:
        """Delete raw face-sample images to reclaim disk space.

        Not needed for day-to-day recognition once trained -- only for
        retraining or adding more samples later, so this is safe to run
        right after a successful train() if you don't plan to do that.
        """
        pattern = f"{student_id}.*.jpg" if student_id is not None else "*.jpg"
        removed = 0
        for path in self.faces_dir.glob(pattern):
            path.unlink()
            removed += 1
        return removed

    def train(self) -> int:
        faces: list[np.ndarray] = []
        ids: list[int] = []
        for path in sorted(self.faces_dir.glob("*.jpg")):
            student_id = int(path.stem.split(".")[0])
            image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                continue
            faces.append(image)
            ids.append(student_id)

        if not faces:
            raise RuntimeError("No face samples found. Capture samples for at least one student first.")

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(ids))
        recognizer.write(str(self.classifier_path))
        return len(faces)

    def load_recognizer(self):
        if not self.classifier_path.exists():
            raise RuntimeError("No trained model found. Train the system before recognizing faces.")
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(str(self.classifier_path))
        return recognizer

    def predict(self, recognizer, gray: np.ndarray, box) -> tuple[int, float]:
        face = self._crop(gray, box)
        student_id, distance = recognizer.predict(face)
        return student_id, distance

    def is_match(self, distance: float) -> bool:
        return distance <= config.MAX_MATCH_DISTANCE

    def find_duplicate(self, gray: np.ndarray, box) -> tuple[int, float] | None:
        """Check a not-yet-registered face against the currently trained model.

        Used before capturing samples for a new student, to warn if this
        face already looks like an existing student rather than silently
        letting the same person get registered twice under different names.
        """
        if not self.classifier_path.exists():
            return None
        recognizer = self.load_recognizer()
        student_id, distance = self.predict(recognizer, gray, box)
        if self.is_match(distance):
            return student_id, distance
        return None
