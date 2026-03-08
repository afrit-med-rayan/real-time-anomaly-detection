"""
backend/streaming/kafka_producer.py
------------------------------------
A thin helper wrapper around confluent-kafka's Producer.

Usage (from other backend modules):
    from backend.streaming.kafka_producer import send_event
    send_event("transactions", event_dict)
"""

import json
import os

from confluent_kafka import Producer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_TRANSACTIONS = "transactions"

_producer: Producer | None = None


def _get_producer() -> Producer:
    """Lazy singleton — creates the producer once on first call."""
    global _producer
    if _producer is None:
        _producer = Producer(
            {
                "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
                "client.id": "anomaly-backend-producer",
                "retries": 5,
                "retry.backoff.ms": 500,
            }
        )
    return _producer


def send_event(topic: str, event: dict, key: str | None = None) -> None:
    """
    Serialize *event* to JSON and produce it to *topic*.

    Parameters
    ----------
    topic : str
        Kafka topic name.
    event : dict
        Event payload — must be JSON-serialisable.
    key : str | None
        Optional message key for Kafka partition routing.
    """
    producer = _get_producer()
    payload = json.dumps(event).encode("utf-8")
    raw_key = key.encode("utf-8") if key else None

    producer.produce(
        topic,
        key=raw_key,
        value=payload,
    )
    producer.poll(0)   # trigger delivery callbacks non-blocking


def flush(timeout: float = 5.0) -> None:
    """Flush outstanding produce requests — call on application shutdown."""
    if _producer is not None:
        _producer.flush(timeout=timeout)
