import cv2
import numpy as np
import pytest

from face_attendance.face_engine import FaceEngine


@pytest.fixture()
def engine(tmp_path):
    return FaceEngine(faces_dir=tmp_path / "faces", classifier_path=tmp_path / "classifier.xml")


def test_train_without_samples_raises(engine):
    with pytest.raises(RuntimeError):
        engine.train()


def test_recognizer_predicts_the_trained_student(engine):
    rng = np.random.default_rng(0)
    box = (0, 0, 200, 200)

    student_a_face = rng.integers(0, 255, size=(200, 200), dtype=np.uint8)
    student_b_face = rng.integers(0, 255, size=(200, 200), dtype=np.uint8)

    engine.save_sample(1, student_a_face, box, sample_index=1)
    engine.save_sample(2, student_b_face, box, sample_index=1)

    trained_count = engine.train()
    assert trained_count == 2
    assert engine.classifier_path.exists()

    recognizer = engine.load_recognizer()
    student_id, distance = engine.predict(recognizer, student_a_face, box)
    assert student_id == 1
    # JPEG re-encoding of the saved sample means this isn't a bit-perfect
    # match, but it should still be much closer than a random face.
    assert distance < 20


def test_largest_face_picks_the_biggest_box(engine):
    faces = [(0, 0, 50, 50), (10, 10, 120, 120), (5, 5, 60, 60)]
    assert tuple(engine.largest_face(faces)) == (10, 10, 120, 120)


def test_largest_face_returns_none_when_empty(engine):
    assert engine.largest_face([]) is None


def test_clear_samples_removes_files(engine):
    rng = np.random.default_rng(1)
    box = (0, 0, 200, 200)
    face = rng.integers(0, 255, size=(200, 200), dtype=np.uint8)

    engine.save_sample(1, face, box, sample_index=1)
    engine.save_sample(1, face, box, sample_index=2)
    engine.save_sample(2, face, box, sample_index=1)

    removed = engine.clear_samples(student_id=1)

    assert removed == 2
    assert engine.sample_count(1) == 0
    assert engine.sample_count(2) == 1


def test_find_duplicate_returns_none_without_a_trained_model(engine):
    rng = np.random.default_rng(2)
    face = rng.integers(0, 255, size=(200, 200), dtype=np.uint8)
    assert engine.find_duplicate(face, (0, 0, 200, 200)) is None


def test_find_duplicate_detects_an_already_registered_face(engine):
    rng = np.random.default_rng(3)
    box = (0, 0, 200, 200)
    registered_face = rng.integers(0, 255, size=(200, 200), dtype=np.uint8)

    engine.save_sample(1, registered_face, box, sample_index=1)
    engine.train()

    match = engine.find_duplicate(registered_face, box)

    assert match is not None
    matched_student_id, distance = match
    assert matched_student_id == 1
    assert distance < 20


def test_eyes_open_does_not_crash_on_a_face_with_no_real_eyes(engine):
    rng = np.random.default_rng(4)
    face = rng.integers(0, 255, size=(200, 200), dtype=np.uint8)
    assert engine.eyes_open(face, (0, 0, 200, 200)) is False


def test_face_size_ok_rejects_a_small_box(engine):
    assert engine.face_size_ok((0, 0, 40, 40)) is False
    assert engine.face_size_ok((0, 0, 200, 200)) is True


def test_sharpness_is_lower_for_a_blurred_face(engine):
    rng = np.random.default_rng(5)
    sharp = rng.integers(0, 255, size=(200, 200), dtype=np.uint8)
    blurred = cv2.GaussianBlur(sharp, (25, 25), 0)
    box = (0, 0, 200, 200)

    assert engine.sharpness(blurred, box) < engine.sharpness(sharp, box)


def test_capture_quality_rejects_a_too_small_face(engine):
    rng = np.random.default_rng(6)
    face = rng.integers(0, 255, size=(200, 200), dtype=np.uint8)
    ok, reason = engine.capture_quality(face, (0, 0, 40, 40))
    assert ok is False
    assert "closer" in reason.lower()
