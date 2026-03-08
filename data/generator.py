"""
data/generator.py
-----------------
Simulates a continuous stream of financial transaction events.

Normal behavior:
  - Amounts between $1 and $500
  - Transaction frequency: 1–10 per hour
  - Account age: 30–3650 days

Anomalies (~5% of events):
  - Massive amounts (>$5000)
  - Impossible frequency (>50/hr)
  - Brand new account (< 3 days)

Events are sent to Kafka topic "transactions" as JSON messages.

Environment variables:
  KAFKA_BOOTSTRAP_SERVERS  (default: localhost:9092)
"""

import json
import os
import random
import time
from datetime import datetime, timezone

from confluent_kafka import Producer

# ─── Config ──────────────────────────────────────────────────────────────────

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = "transactions"
EVENT_INTERVAL_SECONDS = 0.8   # ~75 events/min on average
ANOMALY_PROBABILITY = 0.05     # 5% of events are injected anomalies

LOCATIONS = [
    "Paris", "Berlin", "New York", "Tokyo", "London",
    "Dubai", "Sydney", "Toronto", "Singapore", "Lagos",
]
DEVICE_TYPES = ["mobile", "desktop", "tablet", "POS_terminal"]
MERCHANT_CATEGORIES = [
    "grocery", "electronics", "restaurant", "travel",
    "clothing", "entertainment", "healthcare", "utilities",
]

# ─── Kafka producer ──────────────────────────────────────────────────────────

def create_producer() -> Producer:
    conf = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "client.id": "anomaly-generator",
        # Retry on transient errors so the generator survives Kafka startup lag
        "retries": 10,
        "retry.backoff.ms": 1000,
    }
    return Producer(conf)


def delivery_report(err, msg):
    """Called once per produced message (async confirmation)."""
    if err:
        print(f"[ERROR] Delivery failed: {err}")
    else:
        print(
            f"[OK] → topic={msg.topic()} partition={msg.partition()} "
            f"offset={msg.offset()}"
        )


# ─── Event generation ────────────────────────────────────────────────────────

_transaction_counter = 10_000   # start IDs from 10 000


def _next_id() -> int:
    global _transaction_counter
    _transaction_counter += 1
    return _transaction_counter


def generate_normal_event() -> dict:
    """Generate a synthetic normal transaction."""
    return {
        "transaction_id": _next_id(),
        "user_id": random.randint(100, 9_999),
        "amount": round(random.uniform(1.0, 500.0), 2),
        "location": random.choice(LOCATIONS),
        "device_type": random.choice(DEVICE_TYPES),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "transaction_frequency": random.randint(1, 10),   # per hour
        "account_age": random.randint(30, 3_650),          # days
        "merchant_category": random.choice(MERCHANT_CATEGORIES),
        "is_injected_anomaly": False,
    }


def generate_anomaly_event() -> dict:
    """
    Generate a transaction that contains one or more anomalous signals.
    Three anomaly types are chosen at random or combined.
    """
    event = generate_normal_event()
    event["is_injected_anomaly"] = True

    anomaly_type = random.choice(["high_amount", "high_frequency", "new_account", "combined"])

    if anomaly_type == "high_amount":
        # Extremely high transaction value
        event["amount"] = round(random.uniform(5_000.0, 50_000.0), 2)

    elif anomaly_type == "high_frequency":
        # Impossible burst — hundreds of transactions per hour
        event["transaction_frequency"] = random.randint(50, 200)

    elif anomaly_type == "new_account":
        # Brand-new account making a large purchase
        event["account_age"] = random.randint(0, 2)
        event["amount"] = round(random.uniform(200.0, 1_500.0), 2)

    elif anomaly_type == "combined":
        # Multiple signals at once — hardest to explain innocently
        event["amount"] = round(random.uniform(3_000.0, 20_000.0), 2)
        event["transaction_frequency"] = random.randint(30, 100)
        event["account_age"] = random.randint(0, 5)

    return event


def generate_event() -> dict:
    """Return either a normal or anomalous event based on ANOMALY_PROBABILITY."""
    if random.random() < ANOMALY_PROBABILITY:
        return generate_anomaly_event()
    return generate_normal_event()


# ─── Main loop ───────────────────────────────────────────────────────────────

def main():
    print(f"[Generator] Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS} …")
    producer = create_producer()

    print(f"[Generator] Starting event stream → topic '{TOPIC}' …")
    print(f"[Generator] Anomaly injection rate: {ANOMALY_PROBABILITY * 100:.0f}%")
    print("-" * 60)

    try:
        while True:
            event = generate_event()
            payload = json.dumps(event).encode("utf-8")

            producer.produce(
                TOPIC,
                key=str(event["transaction_id"]).encode("utf-8"),
                value=payload,
                callback=delivery_report,
            )
            # Poll to trigger delivery callbacks without blocking
            producer.poll(0)

            label = "⚠ ANOMALY" if event["is_injected_anomaly"] else "  normal "
            print(
                f"[{label}] id={event['transaction_id']} "
                f"amount=${event['amount']:>10.2f}  "
                f"freq={event['transaction_frequency']:>3}  "
                f"age={event['account_age']:>4}d  "
                f"loc={event['location']}"
            )

            time.sleep(EVENT_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n[Generator] Interrupted by user — flushing remaining messages …")
    finally:
        producer.flush(timeout=10)
        print("[Generator] Done.")


if __name__ == "__main__":
    main()
