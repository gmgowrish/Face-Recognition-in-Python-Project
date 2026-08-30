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
   select them, and click **Capture Face Samples**. Samples are captured
   **automatically** (no need to click for each one) whenever the current
   frame passes a quality gate — face close/large enough, both eyes open,
   not blurry — and the dialog walks you through a guided pose sequence
   (straight, left, right, chin up, chin down) so the training set has some
   angle variety instead of 30 near-identical frames. **Capture Now** forces
   an immediate sample if the quality gate currently passes. It also warns
   if the face already matches a different, already-trained student (to
   catch accidentally registering the same person twice under different
   names).
2. **Train Recognition Model** — trains the LBPH recognizer on every
   captured sample. Re-run this after adding or capturing more students.
   Afterwards it offers to delete the raw sample images to save disk space
   (see "Storage" below).
3. **Take Attendance** — opens a live camera view; a face has to match the
   same student for several consecutive frames ("Verifying...") before it's
   accepted and marked present for the day. Already-marked students get an
   explicit "already marked" message instead of being silently ignored.
4. **Attendance Records** — browse records by date range, select a row to
   see the photo captured at the moment that attendance was marked, and
   export to CSV (includes a `Day` column, and defaults to a date-stamped
   filename like `attendance_2026-08-30_Sunday.csv`).
5. **Dashboard** — monthly analytics, read straight from the database (no
   CSV export/import needed): total check-ins, unique students, average
   per day and best day; a daily check-in trend chart for the month; a
   day-of-week pattern chart; a department breakdown; and a sortable
   per-student roster (days present, attendance rate, last seen). The
   month list and "today" highlight always reflect the current date, so
   there's nothing to regenerate day to day — just reopen it.

Every screen has a **Back** button.

## Configuration

All optional, set as environment variables before running `main.py`:

| Variable | Default | Purpose |
|---|---|---|
| `FACE_ATTENDANCE_DATA_DIR` | `./data` | Where the database, face samples and model are stored |
| `FACE_ATTENDANCE_CAMERA_INDEX` | `0` | OpenCV camera index (`cv2.VideoCapture(index)`) |
| `FACE_ATTENDANCE_SAMPLE_COUNT` | `30` | Face samples captured per student |
| `FACE_ATTENDANCE_MAX_DISTANCE` | `50` | LBPH match threshold (lower = stricter; lower distance = better match) |
| `FACE_ATTENDANCE_CONFIRM_FRAMES` | `8` | Consecutive matching frames required before accepting a recognition |
| `FACE_ATTENDANCE_MIN_OPEN_EYES` | `2` | Eyes that must be detected open to allow capturing a face sample |
| `FACE_ATTENDANCE_MIN_FACE_SIZE` | `150` | Minimum detected face size (px) to auto-capture a sample |
| `FACE_ATTENDANCE_MIN_SHARPNESS` | `60` | Minimum Laplacian-variance sharpness to auto-capture a sample (lower = blurrier allowed) |
| `FACE_ATTENDANCE_CAPTURE_COOLDOWN` | `0.6` | Minimum seconds between auto-captured samples |

## Storage

Face samples are small (200x200 grayscale JPEGs, a few KB each), so even 30
samples/student is only a few hundred KB per student — storage generally
isn't a real concern until you have hundreds of students. That said:

- The raw sample images (`data/faces/`) are **only needed to retrain** (add
  more samples, add new students, or change recognition parameters).
  Day-to-day recognition only reads `data/classifier.xml`, so it's safe to
  delete them once you're done training — the Train screen offers to do
  this for you.
- Deleting a student removes their samples too.
- Attendance photos (`data/attendance_photos/`) are one small JPEG per
  student per day they attended — this grows slowly and predictably over
  time; nothing to clean up unless you want to archive/delete old terms.

## Project layout

```
face_attendance/
├── config.py               # paths + env-driven settings
├── models.py                # SQLAlchemy models: Student, AttendanceRecord
├── db.py                    # engine/session setup
├── face_engine.py           # detection, dataset capture, training, recognition (no GUI dependency)
├── attendance_service.py    # student CRUD, marking/listing/exporting attendance
├── analytics.py             # monthly aggregation for the dashboard (no GUI dependency)
└── ui/
    ├── main_window.py        # menu + entry point
    ├── camera_feed.py         # QTimer-driven webcam polling
    ├── student_dialog.py      # add/delete students, launch capture
    ├── capture_dialog.py      # live preview + auto face sample capture
    ├── train_dialog.py        # runs training on a background thread
    ├── recognize_window.py    # live recognition + auto attendance marking
    ├── attendance_window.py   # records table, date filter, CSV export
    ├── dashboard_window.py    # monthly analytics: KPIs, charts, roster
    └── bar_chart.py           # small QPainter bar chart widget (no charting dependency)
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
- Face crops are histogram-equalized (`cv2.equalizeHist`) before both
  training and prediction, so lighting differences between sessions/rooms
  don't inflate the distance as much.
- Recognition requires several consecutive frames to agree
  (`FACE_ATTENDANCE_CONFIRM_FRAMES`) before it's accepted, and capture
  requires both eyes to be detected open (`FACE_ATTENDANCE_MIN_OPEN_EYES`) —
  this is a basic **quality/liveness gate** (filters blinks, faces turned
  away from the camera, one-off noisy frames), **not real anti-spoofing**.
  Telling a live face apart from a printed photo or a phone screen held up
  to the camera needs texture/depth/motion analysis this Haar+LBPH pipeline
  doesn't do.

### Why it may mislabel faces with very few students enrolled

LBPH is a **nearest-match classifier**, not an open-set one: given a face,
it returns whichever enrolled student is *closest*, even if none of them
are actually a good match. With only one or two students trained, there's
nothing for it to discriminate against, so an unrelated face can still come
back with a low-looking distance. This gets meaningfully better as more
students (and more varied samples — different angles/lighting) are
enrolled, since there's more contrast for LBPH to work with. If false
matches persist, lower `FACE_ATTENDANCE_MAX_DISTANCE` further (e.g. 35-40).
For higher accuracy at scale, swapping in an embedding-based recognizer
(e.g. `face_recognition`/dlib, or a small ONNX face-embedding model) behind
the same `FaceEngine.predict` interface would be the natural next step —
embeddings generalize to unseen/unknown faces far better than LBPH.
