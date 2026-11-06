from __future__ import annotations

import unittest

from pydantic import ValidationError

from app.models import PublishMessageRequest


class PublishMessageRequestTests(unittest.TestCase):
    def test_accepts_a_direct_routing_key_and_json_payload(self) -> None:
        request = PublishMessageRequest(
            routing_key="order.created",
            payload={"order_id": "ORDER-1001", "amount": 99.9},
        )

        self.assertEqual(request.routing_key, "order.created")
        self.assertEqual(request.payload["order_id"], "ORDER-1001")

    def test_rejects_an_invalid_routing_key(self) -> None:
        with self.assertRaises(ValidationError):
            PublishMessageRequest(
                routing_key="order created",
                payload={"order_id": "ORDER-1001"},
            )

    def test_rejects_an_empty_payload(self) -> None:
        with self.assertRaises(ValidationError):
            PublishMessageRequest(routing_key="order.created", payload={})
