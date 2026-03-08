"""
backend/model/predict.py
-------------------------
Loads the trained Isolation Forest model and StandardScaler and provides
a single public function `score_event()` used by the Kafka consumer.

The model returns:
  - anomaly_score : float  [0.0 → 1.0]  higher = more anomalous
  - is_anomaly    : bool   True when score ≥ ANOMALY_THRESHOLD

Isolation Forest's `decision_function()` returns a raw score in
approximately [-0.5, 0.5] where *lower* means *more anomalous*.
We normalise this to [0, 1] with a monotone transform so that
higher values indicate higher anomaly suspicion.
"""

import os
import logging
import numpy as np
import joblib

logger = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────

_MODEL_DIR   = os.path.dirname(os.path.abspath(__file__))
_MODEL_PATH  = os.path.join(_MODEL_DIR, "anomaly_model.pkl")
_SCALER_PATH = os.path.join(_MODEL_DIR, "scaler.pkl")

# ─── Threshold ────────────────────────────────────────────────────────────────

# Normalised score above this value is classified as an anomaly.
# Tune if you want a stricter / more lenient detector.
ANOMALY_THRESHOLD = 0.55

# ─── Lazy-loaded model & scaler ──────────────────────────────────────────────

_model  = None
_scaler = None


def _load_artifacts():
    """Load model and scaler once on first call (lazy init)."""
    global _model, _scaler
    if _model is None:
        if not os.path.exists(_MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {_MODEL_PATH}. "
                "Please run `python backend/model/train_model.py` first."
            )
        logger.info("Loading anomaly model from %s", _MODEL_PATH)
        _model  = joblib.load(_MODEL_PATH)
        _scaler = joblib.load(_SCALER_PATH)
        logger.info("Model and scaler loaded successfully.")


# ─── Feature extraction ───────────────────────────────────────────────────────

FEATURE_KEYS = ["amount", "transaction_frequency", "account_age"]


def _extract_features(event: dict) -> np.ndarray:
    """
    Extract the three numerical features the model was trained on.

    Missing or non-numeric values fall back to sane defaults so the
    consumer never crashes on a malformed event.
    """
    defaults = {"amount": 50.0, "transaction_frequency": 3, "account_age": 365}
    row = [float(event.get(k, defaults[k]) or defaults[k]) for k in FEATURE_KEYS]
    return np.array(row, dtype=np.float64).reshape(1, -1)


# ─── Public API ───────────────────────────────────────────────────────────────

def score_event(event: dict) -> dict:
    """
    Score a single transaction event for anomaly likelihood.

    Parameters
    ----------
    event : dict
        A raw transaction dict (as produced by data/generator.py or
        decoded from a Kafka message).

    Returns
    -------
    dict
        {
            "anomaly_score" : float,   # 0.0 (normal) → 1.0 (very anomalous)
            "is_anomaly"    : bool,    # True when score ≥ ANOMALY_THRESHOLD
        }
    """
    _load_artifacts()

    features = _extract_features(event)
    scaled   = _scaler.transform(features)

    # decision_function: lower raw score ⟹ more anomalous
    raw_score = float(_model.decision_function(scaled)[0])

    # Normalise to [0, 1]:  anomaly_score = 1 − sigmoid(raw * 10)
    # sigmoid maps raw ≈ 0 → 0.5; raw ≪ 0 → 1.0; raw ≫ 0 → 0.0
    normalised = float(1.0 - (1.0 / (1.0 + np.exp(-raw_score * 10))))
    normalised = round(min(max(normalised, 0.0), 1.0), 4)

    is_anomaly = normalised >= ANOMALY_THRESHOLD

    logger.debug(
        "score_event: raw=%.4f normalised=%.4f is_anomaly=%s",
        raw_score, normalised, is_anomaly,
    )

    return {
        "anomaly_score": normalised,
        "is_anomaly": is_anomaly,
    }
