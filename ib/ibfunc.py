from ibapi.execution import ExecutionFilter
import asyncio

from pyIB.ib.ibapp import BasicApp
import threading


class ibfunc():
    # port must match TWS/Gateway API settings
    ibport: int = 4001
    # IB client instance
    ibc: BasicApp = None
    # Thread where the IB EReader will run in the background
    ibMsgThread: threading.Thread

# region === PRIVATE METHODS ===
    def __init__(self):
        print("Creating IB message thread...")
        thread = threading.Thread(group=None, target=self.__spawn__, name="IB")
        thread.start()

        try:
            self.ibc.isConnected()
        except AttributeError:
            pass

        asyncio.run(self.__waitIB__())

    # Used to get around the AttributeError exception
    async def __waitIB__(self):
        handshakeDone = False

        while handshakeDone is False:
            try:
                handshakeDone = self.ibc.isConnected()
            except AttributeError:
                await asyncio.sleep(1)

    def __spawn__(self):
        print("Spawning IB reader (", self.ibport, ")...")
        self.ibc = BasicApp()
        self.ibc.connect("127.0.0.1", self.ibport, 0)
        self.ibc.run()
        # message thread terminated. Disconnect to clean up
        self.ibc.disconnect()
        print("Disconnected from IB")

    # This is used to make sure we only try and execute operations when the client is connected
    def __ibClientOp__(self,fn):
        if self.ibc.isConnected():
            fn()
# endregion

    def getOrders(self):
        print("Getting Orders...")
        self.__ibClientOp__(lambda: self.ibc.reqAllOpenOrders())

    def getExecutions(self):
        print("Getting Executions...")
        filter=ExecutionFilter()
        self.__ibClientOp__(lambda: self.ibc.reqExecutions(100, filter))

def main():
    print("ibfunc.py V1.1")
    a = ibfunc()
    print("pending...")
    print("Connection Status=",a.ibc.isConnected())


if __name__ == '__main__':
    main()
