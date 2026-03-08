"""Quick smoke test for predict.py — run from project root."""
import sys
sys.path.insert(0, ".")
from backend.model.predict import score_event

tests = [
    ("NORMAL",         {"amount": 42.0,      "transaction_frequency": 3,   "account_age": 365}),
    ("ANOMALY-amount", {"amount": 25000.0,   "transaction_frequency": 3,   "account_age": 365}),
    ("ANOMALY-freq",   {"amount": 42.0,      "transaction_frequency": 150, "account_age": 365}),
    ("ANOMALY-age",    {"amount": 800.0,     "transaction_frequency": 3,   "account_age": 1}),
    ("ANOMALY-combo",  {"amount": 12000.0,   "transaction_frequency": 90,  "account_age": 1}),
]

print(f"{'Label':<20} {'Score':>8}  {'Is Anomaly?'}")
print("-" * 45)
for label, event in tests:
    r = score_event(event)
    flag = "⚠  YES" if r["is_anomaly"] else "   no"
    print(f"{label:<20} {r['anomaly_score']:>8.4f}  {flag}")
