# Note: If you get errors where ibapi is not found, go the c:TWS_API.
# In the source->pythonclient, run 'python setup.py install'
# This should resolve any issues
from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.utils import iswrapper
from ibapi.common import *
from ibapi.contract import *
from ibapi.ticktype import *


class BasicApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        print('Error:', reqId, " ", errorCode, " ", errorString)

    @iswrapper
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)
        print("Tick Price. Ticker Id:", reqId, "tickType:", tickType, "Price:", price, "CanAutoExecute:",
              attrib.canAutoExecute, "PastLimit", attrib.pastLimit)

    @iswrapper
    def tickSize(self, reqId: TickerId, tickType: TickType, size: int):
        super().tickSize(reqId, tickType, size)
        print("Tick Size. Ticker Id:", reqId, "tickType:", tickType, "Size:", size)

    @iswrapper
    def tickString(self, reqId: TickerId, tickType: TickType, value: str):
        super().tickString(reqId, tickType, value)
        print("Tick string. Ticker Id:", reqId, "Type:", tickType, "Value:", value)

    @iswrapper
    def tickGeneric(self, reqId: TickerId, tickType: TickType, value: float):
        super().tickGeneric(reqId, tickType, value)
        print("Tick Generic. Ticker Id:", reqId, "tickType:", tickType, "Value:", value)

    @iswrapper
    def openOrderEnd(self):
        super().openOrderEnd();
        print("=== All Orders Retrived ===")

def main():
    app = BasicApp()
    app.connect("127.0.0.1", 7497, 0)
    app.run()
    app.reqOpenOrders(True);
    #contract = Contract();
    #contract.symbol = "VIX";
    #contract.secType = "FUT";
    #contract.exchange = "CFE";
    #contract.currency = "USD";
    #contract.lastTradeDateOrContractMonth = "20170621";
    #app.reqMktData(1001, contract, "", False, False, [])


if __name__ == '__main__':
    main()

