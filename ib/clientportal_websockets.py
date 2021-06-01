# clientportal_websockets.py

from overrides import overrides
from lib.watchdog import Watchdog
import asyncio
import websockets
from lib.certificate import Certificate, CertificateError
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from enum import Enum


class ClientPortalWebsocketsError(Enum):
    Ok = 0
    Unknown = 1
    Invalid_URL = 2
    Invalid_Certificate = 3
    Connection_Failed = 4


# TODO: Document ClientPortalWebsockets class
class ClientPortalWebsockets(Watchdog):
    """
    Interactive Brokers ClientPortal Interface (Websocket).
    Refer to https://interactivebrokers.github.io/cpwebapi/RealtimeSubscription.html for API documentation
    NOTE: Websocket usage also requires the UI to send the /tickle endpoint. See Websocket Ping Session docs.
    """

    connection: websockets.WebSocketClientProtocol

    def __init__(self):
        # Websocket watchdog timer gets a 5-second timeout
        super().__init__(autostart=True, timeout_sec=5, name='IB_WebSocket')
        # Base used by all IB websocket endpoints
        self.url = 'wss://localhost:5000/v1/api/ws'
        self.connection = None
        logger.log('DEBUG', f'Clientportal (Websockets) Started with endpoint: {self.url}')

    def watchdog_task(self):
        super().watchdog_task()
        # TODO: Add periodic call to websocket 'tic'

    async def open_connection(self, url='', url_validator=None):
        """ Open a websocket connection """
        if url_validator is not None:
            if url_validator(url) is False:
                return ClientPortalWebsocketsError.Invalid_URL

        result = Certificate.get_certificate()

        if result.error != CertificateError.Ok:
            logger.log('DEBUG', f'Problems obtaining certificate: {result.error}')
            return ClientPortalWebsocketsError.Invalid_Certificate

        logger.log('DEBUG', f'Opening connection to "{self.url}"')

        try:
            pass
            ws = await websockets.connect(self.url, ssl=result.ssl_context)
        except websockets.WebSocketException as e:
            logger.log('DEBUG', f'Websocket exception: {e}')
        except Exception as e:
            logger.log('DEBUG', f'General exception: {e}')
        finally:
            logger.log('DEBUG', f'Connection established to "{self.url}"')
            self.connection = ws
            pass

        return ClientPortalWebsocketsError.Ok

    async def process_message(self):
        first = False
        if self.connection is not None:
            while True:
                msg = await self.connection.recv()
                print(f'{msg}')
                if first is False:
                    await self.connection.send(
                        'smh+265598+{"exchange":"ISLAND","period":"2h","bar":"5min","outsideRth":false,"source":"t","format":"%h/%l"}')
                    first = True

    def loop(self):
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_connection = executor.submit(
                    asyncio.get_event_loop().run_until_complete(self.open_connection()))
                future_message_handler = executor.submit(
                    asyncio.get_event_loop().run_until_complete(self.process_message()))
        except Exception as e:
            logger.log('DEBUG', f'Exception:{e}')
        finally:
            pass


if __name__ == '__main__':
    print("=== IB Client Portal Websockets ===")