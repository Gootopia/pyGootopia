# clientportal_websockets.py

from overrides import overrides
from ib.watchdog import Watchdog
import asyncio
import websockets
from lib.certificate import Certificate
from loguru import logger
from concurrent.futures import ThreadPoolExecutor


class ClientPortalWebsockets(Watchdog):
    # TODO: Document ClientPortalWebsockets class
    """
    Interactive Brokers ClientPortal Interface (Websocket).
    Refer to https://interactivebrokers.github.io/cpwebapi/RealtimeSubscription.html for API documentation
    NOTE: Websocket usage also requires the UI to send the /tickle endpoint. See Websocket Ping Session docs.
    """
    def __init__(self):
        super().__init__(autostart=True, timeout_sec=5, name='WebSocket')
        self.url_websockets = 'wss://localhost:5000/v1/api/ws'
        # Base used by all endpoints
        logger.log('DEBUG', f'Clientportal (Websockets) Started with endpoint: {self.url_websockets}')

    @overrides
    def watchdog_task(self):
        super().watchdog_task()
        # TODO: Add periodic call to websocket 'tic'

    async def connection(self):
        """ Create the websocket connection """
        ssl_context = Certificate.get_certificate()

        print('Connecting...')
        async with websockets.connect(self.url_websockets, ssl=ssl_context) as ws:
            print('Waiting...')
            await ws.send('smd+265598+{"fields":["31","83"]}')
            while True:
                response = await ws.recv()
                print(f'{response}')

    def loop(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.get_event_loop().run_until_complete(self.connection()))
            print("=== EXITED LOOP ====")


if __name__ == '__main__':
    print("=== IB Client Portal Websockets ===")
