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
        if config.BUNDLED_CASCADE_PATH.exists():
            cascade_path = str(config.BUNDLED_CASCADE_PATH)
        else:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.detector = cv2.CascadeClassifier(cascade_path)
        if self.detector.empty():
            raise RuntimeError(f"Failed to load Haar cascade from {cascade_path}")

    def detect_faces(self, frame_bgr: np.ndarray):
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        return gray, faces

    def largest_face(self, faces):
        if len(faces) == 0:
            return None
        return max(faces, key=lambda box: box[2] * box[3])

    def _crop(self, gray: np.ndarray, box) -> np.ndarray:
        x, y, w, h = box
        return cv2.resize(gray[y : y + h, x : x + w], config.FACE_SAMPLE_SIZE)

    def save_sample(self, student_id: int, gray: np.ndarray, box, sample_index: int) -> Path:
        face = self._crop(gray, box)
        path = self.faces_dir / f"{student_id}.{sample_index}.jpg"
        cv2.imwrite(str(path), face)
        return path

    def sample_count(self, student_id: int) -> int:
        return len(list(self.faces_dir.glob(f"{student_id}.*.jpg")))

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
