# Face Recognition Attendance System

A desktop app that takes attendance by recognizing faces from a webcam feed:
register students, capture face samples, train a recognizer, then point a
camera at a room and attendance gets marked automatically.

This repo has two versions:

| | **Current app** (root) | [`legacy/`](legacy) (original) |
|---|---|---|
| GUI | PyQt6 | Tkinter |
| Database | SQLite (via SQLAlchemy) | MySQL, plaintext credentials, string-built SQL |
| Face detection/recognition | OpenCV Haar cascade + LBPH | OpenCV Haar cascade + LBPH |
| Config | environment variables, relative paths | hardcoded `C:\Users\gmg\...` paths |
| Tests | `pytest` unit tests for the service/engine layer | none |

The legacy version is kept for reference but won't run as-is (Windows-only
paths, a MySQL server it expects at `localhost`, and `Image.ANTIALIAS`, which
Pillow removed years ago). The instructions below are for the current app.

## Requirements

- Python 3.10+
- A webcam
- Linux/macOS/Windows (PyQt6 and OpenCV are cross-platform)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

No database server is needed — data lives in a local SQLite file created
automatically under `data/` on first run:

```
data/
├── attendance.db      # students + attendance records
├── faces/             # captured face samples (per student)
└── classifier.xml     # trained LBPH model
```

## Run in Docker (background)

`run.sh` is the single entry point for building and running the app as a
background container — no need to remember `docker build`/`docker run`
flags:

```bash
./run.sh start     # builds the image if needed, then runs the app detached
./run.sh status    # is it running?
./run.sh logs      # follow output
./run.sh stop       # stop it
./run.sh down       # stop and remove the container
```

`data/` is bind-mounted into the container, so students, face samples and
the trained model persist across restarts and rebuilds.

This is a desktop GUI app, so the container still needs to show a window on
your screen — `run.sh` forwards your `DISPLAY` and the X11 socket into the
container and passes through any `/dev/video*` camera devices it finds.
That means:

- **Linux with X11 (or XWayland, the default on most distros) is required.**
  There is no equivalent on macOS/Windows without extra setup (XQuartz /
  VcXsrv), so on those platforms just run natively (`python main.py`)
  instead.
- The first `start` may need `xhost +local:docker` to let the container
  connect to your X server — `run.sh` attempts this automatically if
  `xhost` is installed.
- If no display or camera is available, `run.sh` still starts the
  container but the window won't be able to render — check `./run.sh logs`.

## Using it

1. **Manage Students** — add a student (roll number, name, department, ...),
   select them, and click **Capture Face Samples** to record ~30 face
   samples from the webcam.
2. **Train Recognition Model** — trains the LBPH recognizer on every
   captured sample. Re-run this after adding or capturing more students.
3. **Take Attendance** — opens a live camera view; recognized faces are
   marked present for the day automatically (once per student per day).
4. **Attendance Records** — browse records by date range and export to CSV.

## Configuration

All optional, set as environment variables before running `main.py`:

| Variable | Default | Purpose |
|---|---|---|
| `FACE_ATTENDANCE_DATA_DIR` | `./data` | Where the database, face samples and model are stored |
| `FACE_ATTENDANCE_CAMERA_INDEX` | `0` | OpenCV camera index (`cv2.VideoCapture(index)`) |
| `FACE_ATTENDANCE_SAMPLE_COUNT` | `30` | Face samples captured per student |
| `FACE_ATTENDANCE_MAX_DISTANCE` | `70` | LBPH match threshold (lower = stricter; lower distance = better match) |

## Project layout

```
face_attendance/
├── config.py               # paths + env-driven settings
├── models.py                # SQLAlchemy models: Student, AttendanceRecord
├── db.py                    # engine/session setup
├── face_engine.py           # detection, dataset capture, training, recognition (no GUI dependency)
├── attendance_service.py    # student CRUD, marking/listing/exporting attendance
└── ui/
    ├── main_window.py        # menu + entry point
    ├── camera_feed.py         # QTimer-driven webcam polling
    ├── student_dialog.py      # add/delete students, launch capture
    ├── capture_dialog.py      # live preview + face sample capture
    ├── train_dialog.py        # runs training on a background thread
    ├── recognize_window.py    # live recognition + auto attendance marking
    └── attendance_window.py   # records table, date filter, CSV export
main.py                      # `python main.py` entry point
tests/                       # pytest tests for the service and engine layers
Dockerfile                   # image definition (Python 3.11-slim + Qt/X11 runtime libs)
run.sh                       # build/start/stop/logs/status for the container
```

`face_engine.py` and `attendance_service.py` have no PyQt6 imports, so the
recognition and attendance logic can be tested without a display or a
camera:

```bash
pip install -e ".[dev]"
pytest
```

## Notes on the recognition approach

Face recognition uses OpenCV's LBPH (Local Binary Patterns Histograms)
recognizer — the same lightweight, dependency-light approach as the
original project, just wired up correctly:

- The Haar cascade ships in `face_attendance/resources/` rather than relying
  on OpenCV's own copy — `opencv-contrib-python`'s wheel doesn't always
  include the data files (confirmed missing on 5.0.0), so `FaceEngine` falls
  back to `cv2.data.haarcascades` only if the bundled file is somehow absent.
- LBPH's `predict()` returns a **distance** (lower = more confident match),
  not a percentage — the original code's `100 * (1 - predict / 300)`
  confidence formula was numerically meaningless. This version thresholds
  on the raw distance instead (`FACE_ATTENDANCE_MAX_DISTANCE`).
- For higher accuracy on larger student populations, swapping in an
  embedding-based recognizer (e.g. `face_recognition`/dlib or a small ONNX
  face embedding model) behind the same `FaceEngine.predict` interface would
  be the natural next step — LBPH is fine for small, controlled datasets.
