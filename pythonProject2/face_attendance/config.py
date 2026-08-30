import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("FACE_ATTENDANCE_DATA_DIR", BASE_DIR / "data"))
FACES_DIR = DATA_DIR / "faces"
CLASSIFIER_PATH = DATA_DIR / "classifier.xml"
DB_PATH = DATA_DIR / "attendance.db"
SNAPSHOT_DIR = DATA_DIR / "attendance_photos"

# Bundled fallback: not every opencv-python(-contrib) build ships the Haar
# cascade data files in cv2.data.haarcascades (observed missing on
# opencv-contrib-python 5.0.0), so we ship known-good copies alongside the
# package and only fall back to cv2's copy if ours is somehow absent.
_RESOURCES_DIR = Path(__file__).resolve().parent / "resources"
BUNDLED_CASCADE_PATH = _RESOURCES_DIR / "haarcascade_frontalface_default.xml"
BUNDLED_EYE_CASCADE_PATH = _RESOURCES_DIR / "haarcascade_eye.xml"

CAMERA_INDEX = int(os.environ.get("FACE_ATTENDANCE_CAMERA_INDEX", "0"))
FACE_SAMPLE_COUNT = int(os.environ.get("FACE_ATTENDANCE_SAMPLE_COUNT", "30"))
FACE_SAMPLE_SIZE = (200, 200)

# LBPH prediction returns a distance, not a percentage: lower means a better
# match. Anything above this is treated as "unknown". LBPH is a nearest-
# match classifier: with only one or two students enrolled it has nothing to
# discriminate against, so a lenient threshold here will label unrelated
# faces with whoever is closest. Lower this further (e.g. 40-45) if that
# happens; raise it only if genuine matches keep showing as "Unknown".
MAX_MATCH_DISTANCE = float(os.environ.get("FACE_ATTENDANCE_MAX_DISTANCE", "50"))

# A single lucky frame shouldn't be enough to mark someone present -- this
# many consecutive frames must all agree on the same match first.
RECOGNITION_CONFIRM_FRAMES = int(os.environ.get("FACE_ATTENDANCE_CONFIRM_FRAMES", "8"))

# A face sample is only accepted for capture/recognition if at least this
# many eyes are detected open in it -- filters out blinks and faces turned
# too far away from the camera. Not a substitute for real anti-spoofing
# (telling a live face apart from a printed photo/phone screen), which needs
# texture/depth/motion analysis this Haar+LBPH pipeline doesn't do.
MIN_OPEN_EYES = int(os.environ.get("FACE_ATTENDANCE_MIN_OPEN_EYES", "2"))

# Auto-capture quality gate for registration samples: reject faces that are
# too small/far (low resolution once resized to FACE_SAMPLE_SIZE) or too
# blurry (motion blur, out of focus) in addition to the eyes-open check.
MIN_FACE_SIZE = int(os.environ.get("FACE_ATTENDANCE_MIN_FACE_SIZE", "150"))
MIN_SHARPNESS = float(os.environ.get("FACE_ATTENDANCE_MIN_SHARPNESS", "60"))

# Minimum time between auto-captured samples, so a session isn't just 30
# near-identical frames of the same instant.
CAPTURE_COOLDOWN_SECONDS = float(os.environ.get("FACE_ATTENDANCE_CAPTURE_COOLDOWN", "0.6"))

# Guided capture sequence: at each point in the capture progress (fraction
# of FACE_SAMPLE_COUNT reached), tell the user what pose to hold. Sampling
# a few different angles instead of only straight-on makes the trained
# model noticeably more robust to how someone actually faces the camera
# day to day.
POSE_GUIDE: list[tuple[float, str]] = [
    (0.0, "Look straight at the camera"),
    (0.2, "Turn your head slightly LEFT"),
    (0.4, "Turn your head slightly RIGHT"),
    (0.6, "Tilt your chin slightly UP"),
    (0.8, "Tilt your chin slightly DOWN"),
]


def ensure_data_dirs() -> None:
    FACES_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
