from ibapi.execution import ExecutionFilter

from pyIB.ib.ibapp import BasicApp
import threading


class ibfunc():
    ibport: int = 4001
    ibc: BasicApp = None
    thread: threading.Thread

    def __init__(self):
        print("=== Creating IB Message Thread...")
        thread = threading.Thread(group=None, target=self.__spawn__, name="IB")
        thread.start()

    def __spawn__(self):
        print("=== Spawning IB Message Thread (", self.ibport, ")")
        self.ibc = BasicApp()
        self.ibc.connect("127.0.0.1", self.ibport, 0)
        self.ibc.run()

    # This is used to make sure we only try and execute operations when the client is connected
    def __ibClientOp__(self,fn):
        if self.ibc.isConnected() == True:
            fn()

    def getOrders(self):
        print("Getting Orders")
        self.__ibClientOp__(lambda: self.ibc.reqAllOpenOrders())

    def getExecutions(self):
        print("Getting Executions")
        self.__ibClientOp__(lambda: self.ibc.reqExecutions(0, ExecutionFilter()))

def main():
    print("ibfunc.py V1.1")
    a = ibfunc()
    print("pending...")
    print("Connection Status=",a.ibc.isConnected())


if __name__ == '__main__':
    main()
