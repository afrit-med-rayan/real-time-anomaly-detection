"""
backend/streaming/kafka_consumer.py
-------------------------------------
Consumes transaction events from the Kafka topic "transactions".

For each message it:
  1. Deserialises the JSON payload.
  2. Passes features to the anomaly scoring model (predict.py).
  3. Stores the enriched result in the in-memory service (anomaly_service.py).
  4. Broadcasts the result to all connected WebSocket clients.

This module is imported and run as an asyncio background task by the
FastAPI server (api/server.py).

Environment variables:
  KAFKA_BOOTSTRAP_SERVERS  (default: localhost:9092)
  KAFKA_GROUP_ID           (default: anomaly-consumer-group)
"""

import asyncio
import json
import os
import logging
from typing import TYPE_CHECKING

from confluent_kafka import Consumer, KafkaException

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "anomaly-consumer-group")
TOPIC = "transactions"
POLL_TIMEOUT_SECONDS = 1.0


def _build_consumer() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": KAFKA_GROUP_ID,
            "auto.offset.reset": "latest",
            "enable.auto.commit": True,
        }
    )


async def consume_events(broadcast_callback=None):
    """
    Async generator that continuously polls Kafka and yields enriched events.

    Parameters
    ----------
    broadcast_callback : coroutine | None
        Optional async callable ``(event_dict) -> None`` invoked for every
        processed event (used by the WebSocket manager to push to clients).

    Runs indefinitely until cancelled.
    """
    # Deferred imports to avoid circular imports at module load time
    from backend.model.predict import score_event
    from backend.services.anomaly_service import store_event

    consumer = _build_consumer()
    consumer.subscribe([TOPIC])
    logger.info("Kafka consumer subscribed to topic '%s'", TOPIC)

    try:
        while True:
            # Non-blocking poll wrapped in asyncio.to_thread so it doesn't
            # block the event loop.
            msg = await asyncio.to_thread(consumer.poll, POLL_TIMEOUT_SECONDS)

            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            try:
                raw = json.loads(msg.value().decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                logger.warning("Skipping unparseable message: %s", exc)
                continue

            # ── Score the event ────────────────────────────────────────────
            result = score_event(raw)
            enriched = {**raw, **result}

            # ── Persist ────────────────────────────────────────────────────
            store_event(enriched)

            # ── Broadcast to WebSocket clients ─────────────────────────────
            if broadcast_callback is not None:
                try:
                    await broadcast_callback(enriched)
                except Exception as exc:   # noqa: BLE001
                    logger.warning("Broadcast error: %s", exc)

            logger.debug(
                "Processed transaction %s | score=%.3f | anomaly=%s",
                enriched.get("transaction_id"),
                enriched.get("anomaly_score", 0),
                enriched.get("is_anomaly"),
            )

    except asyncio.CancelledError:
        logger.info("Kafka consumer task cancelled — shutting down cleanly.")
    finally:
        consumer.close()
        logger.info("Kafka consumer closed.")
