from __future__ import annotations

import numpy as np
import pytest

from src.data.split import stratified_split


def test_stratified_split_default_ratios(sample_X_y) -> None:
    # Arrange
    X, y = sample_X_y  # 30 samples, 3 classes (10 each)

    # Act
    X_train, X_val, X_test, y_train, y_val, y_test = stratified_split(X, y)

    # Assert — 80/10/10 of 30 = 24/3/3
    assert len(X_train) == 24
    assert len(X_val) == 3
    assert len(X_test) == 3
    assert len(X_train) + len(X_val) + len(X_test) == len(X)


def test_stratified_split_preserves_class_distribution(sample_X_y) -> None:
    # Arrange
    X, y = sample_X_y

    # Act
    X_train, _, _, y_train, _, _ = stratified_split(X, y)

    # Assert — each class present in train set
    unique_train = set(y_train)
    unique_all = set(y)
    assert unique_train == unique_all


def test_stratified_split_is_deterministic(sample_X_y) -> None:
    # Arrange
    X, y = sample_X_y

    # Act
    result_a = stratified_split(X, y, seed=7)
    result_b = stratified_split(X, y, seed=7)

    # Assert — same seed → same split
    for arr_a, arr_b in zip(result_a, result_b):
        np.testing.assert_array_equal(arr_a, arr_b)


def test_stratified_split_raises_on_length_mismatch() -> None:
    # Arrange
    X = np.zeros((10, 234), dtype=np.float32)
    y = np.array(["A"] * 5)

    # Act + Assert
    with pytest.raises(ValueError, match="same number of samples"):
        stratified_split(X, y)


def test_stratified_split_raises_on_invalid_ratios(sample_X_y) -> None:
    # Arrange
    X, y = sample_X_y

    # Act + Assert — ratios sum to ≥ 1.0 leaves no training data
    with pytest.raises(ValueError, match="between 0 and 1"):
        stratified_split(X, y, val_ratio=0.6, test_ratio=0.6)
