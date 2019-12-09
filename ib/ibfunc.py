from ib.ibapp import BasicApp
import threading


class ibfunc():
    ibport: int = 4001
    ibc: BasicApp = None
    thread: threading.Thread

    def __init__(self):
        print("=== Creating IB Message Thread...")
        thread = threading.Thread(group=None, target=self.spawn, name="IB")
        thread.start()

    def spawn(self):
        print("=== Spawning IB Message Thread (", self.ibport, ")")
        self.ibc = BasicApp()
        self.ibc.connect("127.0.0.1", self.ibport, 0)
        self.ibc.run()

    def getOrders(self):
        print("Getting Orders")
        self.ibc.reqAllOpenOrders()


def main():
    print("ibfunc.py V1.1")
    a = ibfunc()
    print("pending...")
    a.getOrders()
    print("done")


if __name__ == '__main__':
    main()
