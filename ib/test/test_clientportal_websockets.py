import pytest
from unittest.mock import patch
from asynctest import CoroutineMock
from lib.certificate import CertificateError
from lib.certificate import CertificateReturn
from ib.clientportal_websockets import ClientPortalWebsockets
from ib.clientportal_websockets import ClientPortalWebsocketsError


@patch('ib.clientportal_websockets.Certificate.get_certificate')
class TestClientPortalWebsockets:
    @staticmethod
    def url_validator_ok(url=''):
        """ Simulate checking a URL and finding it valid """
        return True

    @staticmethod
    def url_validator_invalid(url=''):
        """ Simulate checking a URL and finding it bad """
        return False

    @pytest.mark.asyncio
    async def test_open_connection_invalid_url(self, patched):
        cp = ClientPortalWebsockets()
        result = await cp.open_connection(url_validator=TestClientPortalWebsockets.url_validator_invalid)
        assert result == ClientPortalWebsocketsError.Invalid_URL

    @pytest.mark.asyncio
    async def test_open_connection_invalid_certificate(self, patched):
        patched.return_value = CertificateReturn(None, CertificateError.Invalid_Certificate)
        cp = ClientPortalWebsockets()
        result = await cp.open_connection()
        assert result == ClientPortalWebsocketsError.Invalid_Certificate

    @pytest.mark.asyncio
    async def test_open_connection_failed(self, patched):
        patched.return_value = CertificateReturn(None, CertificateError.Ok)
        cp = ClientPortalWebsockets()
        result = await cp.open_connection()
        assert result == ClientPortalWebsocketsError.Invalid_Certificate
