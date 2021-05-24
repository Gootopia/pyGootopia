import pytest
import asyncio
from unittest.mock import MagicMock, patch
from ib.clientportal_websockets import ClientPortalWebsockets
from ib.clientportal_websockets import ClientPortalWebsocketsError


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class TestClientPortalWebsockets:
    @patch("ib.clientportal_websockets.ClientPortalWebsockets.establish_connection",
           return_value=ClientPortalWebsocketsError.Invalid_Certificate,
           new_callable=AsyncMock)
    def test_connection_bad_certificate(self, testpatch):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(ClientPortalWebsockets.establish_connection())
        assert result == ClientPortalWebsocketsError.Invalid_Certificate
