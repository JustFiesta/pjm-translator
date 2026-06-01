from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pytest

from src.model.train import train_and_save


def test_train_and_save_creates_artifact(tmp_path: Path, sample_X_y) -> None:
    # Arrange
    X, y = sample_X_y
    output = tmp_path / "model.pkl"

    # Act
    train_and_save(X, y, output)

    # Assert
    assert output.exists()


def test_train_and_save_artifact_is_loadable(tmp_path: Path, sample_X_y) -> None:
    # Arrange
    X, y = sample_X_y
    output = tmp_path / "model.pkl"
    train_and_save(X, y, output)

    # Act
    clf = joblib.load(output)

    # Assert — loaded model can predict on same-shaped input
    predictions = clf.predict(X[:3])
    assert predictions.shape == (3,)
    assert all(p in set(y) for p in predictions)


def test_train_and_save_creates_parent_dirs(tmp_path: Path, sample_X_y) -> None:
    # Arrange
    X, y = sample_X_y
    nested_output = tmp_path / "nested" / "dir" / "model.pkl"

    # Act
    train_and_save(X, y, nested_output)

    # Assert
    assert nested_output.exists()


def test_train_and_save_raises_on_length_mismatch() -> None:
    # Arrange
    X = np.zeros((10, 234), dtype=np.float32)
    y = np.array(["A"] * 5)

    # Act + Assert
    with pytest.raises(ValueError, match="same length"):
        train_and_save(X, y, Path("artifacts/model.pkl"))
