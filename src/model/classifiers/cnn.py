from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_IMG_SIZE = 28

try:  # pragma: no cover - optional dependency path
    import tensorflow as tf
except ImportError:  # pragma: no cover
    tf = None


class CnnPredictor:
    """Adapter exposing ``predict`` for a trained Keras CNN model."""

    def __init__(self, model: object, labels: list[str]) -> None:
        self._model = model
        self._labels = labels

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels for flattened 28x28 grayscale vectors.

        Args:
            X: Feature matrix of shape ``(n_samples, 784)``.

        Returns:
            Array of predicted label strings of shape ``(n_samples,)``.
        """
        if tf is None:  # pragma: no cover
            raise RuntimeError(
                "TensorFlow is required for CNN inference. "
                "Install it first and retry."
            )
        X_img = X.reshape(-1, _IMG_SIZE, _IMG_SIZE, 1).astype(np.float32)
        probs = self._model.predict(X_img, verbose=0)
        pred_ids = np.argmax(probs, axis=1)
        return np.array([self._labels[i] for i in pred_ids], dtype=object)


def _check_tensorflow() -> None:
    if tf is None:
        raise RuntimeError(
            "TensorFlow is required for CNN training/inference. "
            "Install it first and retry."
        )


def _build_cnn(num_classes: int) -> object:
    """Build a classic CNN for 28x28 grayscale images."""
    _check_tensorflow()
    assert tf is not None
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(_IMG_SIZE, _IMG_SIZE, 1)),
            tf.keras.layers.Conv2D(32, kernel_size=3, activation="relu"),
            tf.keras.layers.MaxPooling2D(pool_size=2),
            tf.keras.layers.Conv2D(64, kernel_size=3, activation="relu"),
            tf.keras.layers.MaxPooling2D(pool_size=2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(num_classes, activation="softmax"),
        ]
    )
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train_and_save_cnn(
    X_train: np.ndarray,
    y_train: np.ndarray,
    model_path: Path,
    labels_path: Path,
    epochs: int = 8,
    batch_size: int = 64,
) -> None:
    """Train a CNN on flattened 28x28 vectors and save artifacts.

    Args:
        X_train: Feature matrix of shape ``(n_samples, 784)``.
        y_train: Label array of shape ``(n_samples,)``.
        model_path: Destination ``.keras`` file path.
        labels_path: Destination JSON path for class label mapping.
        epochs: Number of training epochs.
        batch_size: Training batch size.
    """
    _check_tensorflow()
    assert tf is not None

    labels = sorted({str(label) for label in y_train})
    label_to_id = {label: idx for idx, label in enumerate(labels)}
    y_ids = np.array([label_to_id[str(label)] for label in y_train], dtype=np.int32)
    X_img = X_train.reshape(-1, _IMG_SIZE, _IMG_SIZE, 1).astype(np.float32)

    model = _build_cnn(num_classes=len(labels))
    model.fit(X_img, y_ids, epochs=epochs, batch_size=batch_size, verbose=1)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(model_path)
    labels_path.write_text(json.dumps(labels), encoding="utf-8")


def load_cnn_predictor(model_path: Path, labels_path: Path) -> CnnPredictor:
    """Load CNN artifacts and return a predictor compatible with ``predict_sign``."""
    _check_tensorflow()
    assert tf is not None

    if not model_path.exists():
        raise FileNotFoundError(f"CNN model artifact not found: {model_path}")
    if not labels_path.exists():
        raise FileNotFoundError(f"CNN labels mapping not found: {labels_path}")

    model = tf.keras.models.load_model(model_path)
    labels = json.loads(labels_path.read_text(encoding="utf-8"))
    return CnnPredictor(model=model, labels=labels)
