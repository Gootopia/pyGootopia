# clientportal_websockets.py

import asyncio
import websockets
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from lib.certificate import Certificate, CertificateError
from loguru import logger
from eventhandler import EventHandler


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

    def __init__(self):
        self.event_handler = EventHandler('onConnection')
        self.event_handler.link(self.__on_connection, 'onConnection')

        # Base used by all IB websocket endpoints
        self.url = 'wss://localhost:5000/v1/api/ws'
        self.connection = None
        logger.log('DEBUG', f'Clientportal (Websockets) Started with endpoint: {self.url}')

    def __on_connection(self):
        print('Get your self connected!')

    async def open_connection(self, url='', url_validator=None):
        """ Open a websocket connection """
        if url_validator is not None:
            if url_validator(url) is False:
                return ClientPortalWebsocketsError.Invalid_URL

        try:
            logger.log('DEBUG', f'Certificate: Acquiring')
            result = Certificate.get_certificate()

        except Exception as e:
            logger.log('DEBUG', f'EXCEPTION: {e}')
            return ClientPortalWebsocketsError.Unknown

        finally:
            if result.error != CertificateError.Ok:
                logger.log('DEBUG', f'Certificate: Problems obtaining certificate: {result.error}')
                return ClientPortalWebsocketsError.Invalid_Certificate

        try:
            logger.log('DEBUG', f'Connection: Opening "{self.url}"')
            ret_code = ClientPortalWebsocketsError.Ok
            self.connection = await websockets.connect(self.url, ssl=result.ssl_context)
            logger.log('DEBUG', f'Connection: Established "{self.url}"')
            self.event_handler.fire("onConnection")

            # Once connection is achieved, IB provides confirmation with username
            connect_msg = await self.connection.recv()
            logger.log('DEBUG', f'Connection: Confirmation {connect_msg}')

        except websockets.WebSocketException as e:
            logger.log('DEBUG', f'EXCEPTION: Websockets {e}')
            ret_code = ClientPortalWebsocketsError.Connection_Failed

        except Exception as e:
            logger.log('DEBUG', f'EXCEPTION: General exception: {e}')
            ret_code = ClientPortalWebsocketsError.Unknown

        finally:
            return ret_code

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
            logger.log('DEBUG', f'Websocket: Start message handler')
            try:
                while True:
                    msg = await self.connection.recv()
                    print(f'{msg}')

            except Exception as e:
                logger.log('DEBUG', f'EXCEPTION: {e}')

            finally:
                logger.log('DEBUG', f'Websocket: Exited message handler')

        else:
            logger.log('DEBUG', f'Websocket: Handler has no valid connection')

    async def __websocket_realtime(self):
        if self.connection is not None:
            print('Realtime')
            r = await self.connection.send('smd+265598+{"fields":["31"]}')
            r = await self.connection.send('smd+412889032+{"fields":["31"]}')
            print(f'{r}')

    async def __websocket_heartbeat(self):
        if self.connection is not None:
            logger.log('DEBUG', f'Websocket: Started heartbeat')

            try:
                while True:
                    await self.connection.send('tic')
                    await asyncio.sleep(60)

            except Exception as e:
                logger.log('DEBUG', f'EXCEPTION: {e}')

            finally:
                logger.log('DEBUG', f'Exited websocket heartbeat')

    async def __async_loop(self):
        try:
            task_connection = asyncio.create_task(self.open_connection())
            # msg_handler and heartbeat depend on opening a valid connection
            ret = await task_connection
            print('Starting Other Tasks')
            if ret == ClientPortalWebsocketsError.Ok:
                status = await asyncio.gather(self.__websocket_msg_handler(), self.__websocket_heartbeat(), self.__websocket_realtime())

        except Exception as e:
            logger.log('DEBUG', f'EXCEPTION: {e}')

        finally:
            logger.log('DEBUG', f'Websocket: Exited loop')


if __name__ == '__main__':
    print("=== IB Client Portal Websockets ===")