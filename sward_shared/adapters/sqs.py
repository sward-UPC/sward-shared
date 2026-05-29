import json
import logging
from typing import Any

import boto3

from sward_shared.events.event_envelope import EventEnvelope

logger = logging.getLogger(__name__)


class SqsAdapter:
    def __init__(self, queue_url: str, region: str = "us-east-1"):
        self._queue_url = queue_url
        self._client = boto3.client("sqs", region_name=region)

    def send_message(self, envelope: EventEnvelope) -> None:
        body = json.dumps(
            {
                "id": str(envelope.id),
                "correlation_id": envelope.correlation_id,
                "payload_json": envelope.payload_json,
                "retry_count": envelope.retry_count,
            }
        )
        self._client.send_message(QueueUrl=self._queue_url, MessageBody=body)
        logger.info("SQS mensaje enviado | queue=%s", self._queue_url)

    def receive_messages(self, max_messages: int = 10) -> list[dict[str, Any]]:
        response = self._client.receive_message(
            QueueUrl=self._queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=5,
        )
        return response.get("Messages", [])
