from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier


def build_random_forest_classifier() -> RandomForestClassifier:
    """Build the default RandomForest classifier for sign classification."""
    return RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42)
