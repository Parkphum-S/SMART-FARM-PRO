import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, "backend")

from app import lifespan


@pytest.mark.asyncio
async def test_lifespan_manages_mqtt_client():
    app = object()
    with patch("app.mqtt_client.connect") as connect, patch("app.mqtt_client.disconnect") as disconnect:
        async with lifespan(app):
            connect.assert_called_once()
            disconnect.assert_not_called()
        disconnect.assert_called_once()
