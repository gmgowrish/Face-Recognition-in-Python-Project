import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("FACE_ATTENDANCE_DATA_DIR", BASE_DIR / "data"))
FACES_DIR = DATA_DIR / "faces"
CLASSIFIER_PATH = DATA_DIR / "classifier.xml"
DB_PATH = DATA_DIR / "attendance.db"

# Bundled fallback: not every opencv-python(-contrib) build ships the Haar
# cascade data files in cv2.data.haarcascades (observed missing on
# opencv-contrib-python 5.0.0), so we ship a known-good copy alongside the
# package and only fall back to cv2's copy if ours is somehow absent.
BUNDLED_CASCADE_PATH = Path(__file__).resolve().parent / "resources" / "haarcascade_frontalface_default.xml"

CAMERA_INDEX = int(os.environ.get("FACE_ATTENDANCE_CAMERA_INDEX", "0"))
FACE_SAMPLE_COUNT = int(os.environ.get("FACE_ATTENDANCE_SAMPLE_COUNT", "30"))
FACE_SAMPLE_SIZE = (200, 200)

# LBPH prediction returns a distance, not a percentage: lower means a better
# match. Anything above this is treated as "unknown".
MAX_MATCH_DISTANCE = float(os.environ.get("FACE_ATTENDANCE_MAX_DISTANCE", "70"))


def ensure_data_dirs() -> None:
    FACES_DIR.mkdir(parents=True, exist_ok=True)
