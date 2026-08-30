#!/usr/bin/env bash
# Single entry point to build, run (in the background), and manage the
# Face Recognition Attendance System container.
#
# Usage: ./run.sh <command>
#   build     Build the Docker image
#   start     Start the app in the background (builds the image first if missing)
#   stop      Stop the running container
#   restart   Stop then start
#   status    Show whether the container is running
#   logs      Follow the app's logs
#   shell     Open a shell inside the running container
#   down      Stop and remove the container
set -euo pipefail

IMAGE_NAME="face-attendance:latest"
CONTAINER_NAME="face_attendance_app"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/data"

log() { echo "[run.sh] $*"; }

build() {
    log "Building image ${IMAGE_NAME}..."
    docker build -t "${IMAGE_NAME}" "${SCRIPT_DIR}"
}

image_exists() {
    docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1
}

container_running() {
    [ "$(docker ps -q -f name="^${CONTAINER_NAME}\$")" != "" ]
}

container_exists() {
    [ "$(docker ps -aq -f name="^${CONTAINER_NAME}\$")" != "" ]
}

camera_args() {
    local args=()
    for dev in /dev/video*; do
        [ -e "$dev" ] && args+=(--device "${dev}:${dev}")
    done
    printf '%s\n' "${args[@]}"
}

start() {
    if container_running; then
        log "${CONTAINER_NAME} is already running."
        return 0
    fi
    image_exists || build

    if container_exists; then
        log "Removing previous (stopped) container..."
        docker rm "${CONTAINER_NAME}" >/dev/null
    fi

    mkdir -p "${DATA_DIR}"

    # On SELinux-enforcing hosts (Fedora/RHEL/CentOS), the container's root
    # is denied access to the bind-mounted data dir *and* the X11 socket
    # even though it looks like a plain permission error. Relabeling each
    # mount (:Z/:z) is the textbook fix, but in practice it did not clear
    # the X11 AVC denial here -- disabling SELinux confinement for this one
    # container did. That's a real (if narrow) security trade-off: this
    # container runs unconfined by SELinux so it can reach your X server.
    local selinux_args=()
    if command -v getenforce >/dev/null 2>&1 && [ "$(getenforce)" = "Enforcing" ]; then
        selinux_args=(--security-opt label=disable)
    fi

    local display_args=()
    if [ -n "${DISPLAY:-}" ] && [ -d /tmp/.X11-unix ]; then
        command -v xhost >/dev/null 2>&1 && xhost +local:root >/dev/null 2>&1 || true
        display_args=(-e "DISPLAY=${DISPLAY}" -v /tmp/.X11-unix:/tmp/.X11-unix:rw)
    else
        log "WARNING: no DISPLAY detected. The GUI window will not be able to show." >&2
        log "This only works on a Linux host running an X server (X11/XWayland)." >&2
    fi

    mapfile -t cam_args < <(camera_args)

    log "Starting ${CONTAINER_NAME} in the background..."
    docker run -d \
        --name "${CONTAINER_NAME}" \
        --restart unless-stopped \
        "${selinux_args[@]}" \
        "${display_args[@]}" \
        "${cam_args[@]}" \
        -v "${DATA_DIR}:/app/data:rw" \
        "${IMAGE_NAME}" >/dev/null

    log "Started. Use './run.sh logs' to follow output or './run.sh status' to check state."
}

stop() {
    if container_running; then
        log "Stopping ${CONTAINER_NAME}..."
        docker stop "${CONTAINER_NAME}" >/dev/null
    else
        log "${CONTAINER_NAME} is not running."
    fi
}

down() {
    stop
    if container_exists; then
        docker rm "${CONTAINER_NAME}" >/dev/null
        log "Removed ${CONTAINER_NAME}."
    fi
}

status() {
    if container_running; then
        log "${CONTAINER_NAME} is running."
        docker ps -f name="^${CONTAINER_NAME}\$"
    elif container_exists; then
        log "${CONTAINER_NAME} exists but is stopped."
    else
        log "${CONTAINER_NAME} has not been created yet."
    fi
}

logs() {
    docker logs -f "${CONTAINER_NAME}"
}

shell() {
    docker exec -it "${CONTAINER_NAME}" bash
}

case "${1:-}" in
    build)   build ;;
    start)   start ;;
    stop)    stop ;;
    restart) stop; start ;;
    status)  status ;;
    logs)    logs ;;
    shell)   shell ;;
    down)    down ;;
    *)
        echo "Usage: $0 {build|start|stop|restart|status|logs|shell|down}" >&2
        exit 1
        ;;
esac
