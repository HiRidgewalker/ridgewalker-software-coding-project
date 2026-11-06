from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from app.settings import Settings
from app.topology import declare_topology


class TopologyDeclarationTests(unittest.TestCase):
    def test_declares_exchange_queue_and_binding_with_fixed_settings(self) -> None:
        settings = Settings(
            rabbitmq_exchange="orders.direct",
            rabbitmq_queue="orders.created.queue",
            rabbitmq_binding_key="order.created",
        )
        connection = Mock()
        connection.is_open = True
        channel = connection.channel.return_value

        with patch("app.topology.create_connection", return_value=connection):
            declare_topology(settings)

        channel.exchange_declare.assert_called_once_with(
            exchange="orders.direct",
            exchange_type="direct",
            durable=True,
        )
        channel.queue_declare.assert_called_once_with(
            queue="orders.created.queue",
            durable=True,
        )
        channel.queue_bind.assert_called_once_with(
            queue="orders.created.queue",
            exchange="orders.direct",
            routing_key="order.created",
        )
        connection.close.assert_called_once()
