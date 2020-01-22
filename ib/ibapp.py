# Note: If you get errors where ibapi is not found, go the c:TWS_API.
# In the source->pythonclient, run 'python setup.py install'
# This should resolve any issues
from ibapi.execution import Execution
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.utils import iswrapper
from ibapi.common import *
from ibapi.contract import *
from ibapi.ticktype import *


class BasicApp(EWrapper, EClient):
    # next valid id for submitting requests to IB
    __nextId__:int = 0

    # auto increment of reqId required for each request submission
    def getReqId(self):
        nextId = self.__nextId__
        self.__nextId__ = nextId + 1

#region Constructor
    def __init__(self):
        print("Creating IB EClient...")
        EClient.__init__(self, self)
        print("IB EClient created.")
#endregion

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        print('Error:', reqId, " ", errorCode, " ", errorString)

    def nextValidId(self, orderId: int):
        print("Next Valid ID:", orderId)
        self.__nextId__ = orderId

    # Anything that has to do with IB price data
    # region IB Tick Events
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

    # endregion

    @iswrapper
    def openOrder(self, orderId: int, contract: Contract, order: Order, orderstate: OrderState):
        print("OrderId=", orderId, "Symbol=", contract.symbol, "OrderState=", orderstate.status)

    @iswrapper
    def openOrderEnd(self):
        super().openOrderEnd()
        print("=== All Orders Retrived ===")

    # Anything to do with IB order management and executions
    # region IB Order&Execution Events
    @iswrapper
    def execDetails(self, reqId: int, contract: Contract, execution: Execution):
        super().execDetails(reqId,contract,execution)
        print("ExecDetails. ReqId:", reqId, "Symbol:", contract.symbol, "SecType:", contract.secType, "Currency:",
              contract.currency, execution)

    @iswrapper
    def execDetailsEnd(self, reqId:int):
        print("=== All Executions Retrieved ===")
    # endregion

def main():
    print("ibapp.py V1.0");


if __name__ == '__main__':
    main()
