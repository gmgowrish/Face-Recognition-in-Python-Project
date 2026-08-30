FROM python:3.11-slim

# Runtime libraries the Qt "xcb" platform plugin and OpenCV need to talk to
# an X server and a webcam from inside the container.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libegl1 \
    libopengl0 \
    libglib2.0-0 \
    libsm6 \
    libice6 \
    libxext6 \
    libxrender1 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY face_attendance ./face_attendance

ENV FACE_ATTENDANCE_DATA_DIR=/app/data
VOLUME ["/app/data"]

CMD ["python", "main.py"]
