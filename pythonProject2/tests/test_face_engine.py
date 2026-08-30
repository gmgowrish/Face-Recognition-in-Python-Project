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
