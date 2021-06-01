# clientportal_websockets.py

from overrides import overrides
from lib.watchdog import Watchdog
import asyncio
import websockets
from lib.certificate import Certificate, CertificateError
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import time


class ClientPortalWebsocketsError(Enum):
    Ok = 0
    Unknown = 1
    Invalid_URL = 2
    Invalid_Certificate = 3
    Connection_Failed = 4


# TODO: Document ClientPortalWebsockets class
class ClientPortalWebsockets():
    """
    Interactive Brokers ClientPortal Interface (Websocket).
    Refer to https://interactivebrokers.github.io/cpwebapi/RealtimeSubscription.html for API documentation
    NOTE: Websocket usage also requires the UI to send the /tickle endpoint. See Websocket Ping Session docs.
    """

    connection: websockets.WebSocketClientProtocol

    def __init__(self):
        # Base used by all IB websocket endpoints
        self.url = 'wss://localhost:5000/v1/api/ws'
        self.connection = None
        logger.log('DEBUG', f'Clientportal (Websockets) Started with endpoint: {self.url}')

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

    def loop(self):
        """ Start websocket message handler and heartbeat """
        try:
            with ThreadPoolExecutor() as executor:
                executor.submit(asyncio.get_event_loop().run_until_complete(self.__async_loop()))

        except Exception as e:
            logger.log('DEBUG', f'Exception:{e}')
        finally:
            pass

    async def __websocket_msg_handler(self):
        if self.connection is not None:
            logger.log('DEBUG', f'Started websocket message handler')
            try:
                while True:
                    msg = await self.connection.recv()
                    print(f'{msg}')
            except Exception as e:
                logger.log('DEBUG', f'Exception: {e}')

        else:
            logger.log('DEBUG', f'Websocket handler has no valid connection')

    async def __websocket_heartbeat(self):
        if self.connection is not None:
            logger.log('DEBUG', f'Started websocket heartbeat')
            try:
                while True:
                    await self.connection.send('tic')
                    await asyncio.sleep(10)
            except Exception as e:
                logger.log('DEBUG', f'Exception: {e}')

    async def __async_loop(self):
        task_connection = asyncio.create_task(self.open_connection())
        await task_connection
        await asyncio.gather(self.__websocket_msg_handler(), self.__websocket_heartbeat())


if __name__ == '__main__':
    print("=== IB Client Portal Websockets ===")