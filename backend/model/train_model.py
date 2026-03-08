"""
backend/model/train_model.py
-----------------------------
Trains an Isolation Forest anomaly detection model on synthetic normal
transaction data and exports the trained model as anomaly_model.pkl.

Usage:
    cd c:\\Users\\asus\\real-time-anomaly-detection\\backend
    python model/train_model.py

Output:
    backend/model/anomaly_model.pkl   — trained model
    backend/model/scaler.pkl          — feature scaler (StandardScaler)

Features used:
    [amount, transaction_frequency, account_age]
"""

import os
import random
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

# ─── Config ──────────────────────────────────────────────────────────────────

RANDOM_STATE   = 42
N_TRAIN        = 12_000   # normal training samples
N_EVAL_NORMAL  = 2_000    # normal samples for evaluation
N_EVAL_ANOMALY = 500      # injected anomaly samples for evaluation
CONTAMINATION  = 0.05     # expected 5% anomaly rate

MODEL_DIR  = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(MODEL_DIR, "anomaly_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

# ─── Feature bounds (mirror generator.py) ────────────────────────────────────

# Normal ranges
NORMAL_AMOUNT_MIN   = 1.0
NORMAL_AMOUNT_MAX   = 500.0
NORMAL_FREQ_MIN     = 1
NORMAL_FREQ_MAX     = 10
NORMAL_AGE_MIN      = 30
NORMAL_AGE_MAX      = 3_650

# Anomaly ranges
ANOMALY_AMOUNT_MIN  = 5_000.0
ANOMALY_AMOUNT_MAX  = 50_000.0
ANOMALY_FREQ_MIN    = 50
ANOMALY_FREQ_MAX    = 200
ANOMALY_AGE_MIN     = 0
ANOMALY_AGE_MAX     = 2

# ─── Data generation helpers ─────────────────────────────────────────────────

rng = np.random.default_rng(RANDOM_STATE)


def _normal_samples(n: int) -> np.ndarray:
    """Generate *n* normal [amount, frequency, age] samples."""
    amount = rng.uniform(NORMAL_AMOUNT_MIN, NORMAL_AMOUNT_MAX, n)
    freq   = rng.integers(NORMAL_FREQ_MIN, NORMAL_FREQ_MAX + 1, n).astype(float)
    age    = rng.integers(NORMAL_AGE_MIN,  NORMAL_AGE_MAX + 1,  n).astype(float)
    return np.column_stack([amount, freq, age])


def _anomaly_samples(n: int) -> np.ndarray:
    """Generate *n* anomalous samples (mix of three anomaly patterns)."""
    per_type = n // 3
    remainder = n - per_type * 3

    # High-amount anomalies
    a1 = np.column_stack([
        rng.uniform(ANOMALY_AMOUNT_MIN, ANOMALY_AMOUNT_MAX, per_type),
        rng.integers(NORMAL_FREQ_MIN, NORMAL_FREQ_MAX + 1, per_type).astype(float),
        rng.integers(NORMAL_AGE_MIN, NORMAL_AGE_MAX + 1, per_type).astype(float),
    ])

    # High-frequency anomalies
    a2 = np.column_stack([
        rng.uniform(NORMAL_AMOUNT_MIN, NORMAL_AMOUNT_MAX, per_type),
        rng.integers(ANOMALY_FREQ_MIN, ANOMALY_FREQ_MAX + 1, per_type).astype(float),
        rng.integers(NORMAL_AGE_MIN, NORMAL_AGE_MAX + 1, per_type).astype(float),
    ])

    # New-account anomalies
    a3 = np.column_stack([
        rng.uniform(200.0, 1_500.0, per_type + remainder),
        rng.integers(NORMAL_FREQ_MIN, NORMAL_FREQ_MAX + 1, per_type + remainder).astype(float),
        rng.integers(ANOMALY_AGE_MIN, ANOMALY_AGE_MAX + 1, per_type + remainder).astype(float),
    ])

    return np.vstack([a1, a2, a3])


# ─── Main ─────────────────────────────────────────────────────────────────────

def train_and_export():
    print("=" * 60)
    print(" Isolation Forest — Anomaly Detection Model Training")
    print("=" * 60)

    # ── 1. Generate training data (normal only) ────────────────────────────
    print(f"\n[1/5] Generating {N_TRAIN} normal training samples …")
    X_train = _normal_samples(N_TRAIN)
    print(f"      X_train shape: {X_train.shape}")

    # ── 2. Fit StandardScaler ──────────────────────────────────────────────
    print("\n[2/5] Fitting StandardScaler …")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # ── 3. Train Isolation Forest ──────────────────────────────────────────
    print(f"\n[3/5] Training IsolationForest (n_estimators=200, contamination={CONTAMINATION}) …")
    model = IsolationForest(
        n_estimators=200,
        contamination=CONTAMINATION,
        max_samples="auto",
        random_state=RANDOM_STATE,
        verbose=0,
    )
    model.fit(X_train_scaled)
    print("      Training complete.")

    # ── 4. Evaluate on hold-out set ────────────────────────────────────────
    print(f"\n[4/5] Evaluating on {N_EVAL_NORMAL} normal + {N_EVAL_ANOMALY} anomaly samples …")
    X_eval_normal  = _normal_samples(N_EVAL_NORMAL)
    X_eval_anomaly = _anomaly_samples(N_EVAL_ANOMALY)

    X_eval  = np.vstack([X_eval_normal, X_eval_anomaly])
    y_true  = np.concatenate([
        np.ones(N_EVAL_NORMAL),   # +1 = normal  (sklearn convention)
        -np.ones(N_EVAL_ANOMALY), # -1 = anomaly
    ])

    X_eval_scaled = scaler.transform(X_eval)
    y_pred = model.predict(X_eval_scaled)   # +1 normal / -1 anomaly

    # Remap to human-readable labels
    label_map = {1: "normal", -1: "anomaly"}
    y_true_labels = [label_map[v] for v in y_true.astype(int)]
    y_pred_labels = [label_map[v] for v in y_pred.astype(int)]

    print("\n      Classification Report:")
    print(classification_report(y_true_labels, y_pred_labels, digits=3))

    # ── 5. Export model ────────────────────────────────────────────────────
    print(f"[5/5] Exporting model → {MODEL_PATH}")
    joblib.dump(model, MODEL_PATH)
    print(f"      Exporting scaler → {SCALER_PATH}")
    joblib.dump(scaler, SCALER_PATH)
    print("\n✅ Done — model and scaler saved successfully.")
    print("=" * 60)


if __name__ == "__main__":
    train_and_export()
