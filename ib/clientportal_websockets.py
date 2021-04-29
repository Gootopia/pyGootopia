# clientportal_websockets.py

from overrides import overrides
from ib.clientportal_http import ClientPortalHttp
import asyncio
import websockets
import pathlib
import ssl

from loguru import logger


class ClientPortalWebsockets(ClientPortalHttp):
    # TODO: Document ClientPortalWebsockets class
    """
    Interactive Brokers ClientPortal Interface (Websocket).
    Refer to https://interactivebrokers.github.io/cpwebapi/RealtimeSubscription.html for API documentation
    """
    def __init__(self):
        super().__init__()
        self.url_websockets = 'wss://localhost:5000/v1/api/ws'
        # Base used by all endpoints
        logger.log('DEBUG', f'Clientportal (Websockets) Started with endpoint: {self.url_websockets}')

    @overrides
    def watchdog_task(self):
        # call the http watchdog which is also required to keep alive the websockets sessions
        super().watchdog_task()

    async def connection(self):
        ''' Create the websocket connection
        This seems to require a certificate and there are many options which can be used on line #1
        See:
        https://talkdotnet.wordpress.com/2019/08/07/generating-a-pem-private-and-public-certificate-with-openssl-on-windows/
        Perform the following in the same directory as this .py module
        1) openssl req -x509 -newkey rsa:4096 -keyout {keyname}.pem -out {publickey_name}.pem -nodes
        2) openssl x509 -outform der -in {publickey_name}.pem -out {publickey_name}.crt
        '''
        ssl_context = ssl.SSLContext(ssl.CERT_REQUIRED)
        localhost_pem = pathlib.Path(__file__).with_name("keytest_public.pem")
        ssl_context.load_verify_locations(localhost_pem)

        print('Connecting...')
        async with websockets.connect(self.url_websockets, ssl=ssl_context) as ws:
            print('Waiting...')
            await ws.send('smd+265598+{"fields":["31","83"]}')
            response = await ws.recv()
            print(f'{response}')

    def loop(self):
        asyncio.get_event_loop().run_until_complete(self.connection())


if __name__ == '__main__':
    print("=== IB Client Portal Websockets ===")
