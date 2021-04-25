# ibclientport.py
# IB Client Portal for REST requests. Use ClientPortalWS to add websocket functionality
# Refer to https://www.interactivebrokers.com/api/doc.html for API documentation
# Swagger can be used to test client requests: https://interactivebrokers.github.io/cpwebapi/swagger-ui.html
# Consult curl.trillworks.com for conversion of curl commands to Python requests

from overrides import overrides
from ib.endpoints import Endpoints
from ib.httpendpoints import HttpEndpoints


class ClientPortal(HttpEndpoints):
    # constructor
    def __init__(self):
        super().__init__()
        # Set the base used by all endpoints
        self.set_urlbase('https://localhost:5000/v1/portal')

    @overrides
    def watchdog_task(self):
        print("=== IB HEARTBEAT ===")

    # Session->Ping = Ping the server to keep session open
    def clientrequest_ping(self):
        return self.clientrequest_post(self, Endpoints.Ping.value)

    # Session->Authentication Status = Request to get client status
    def clientrequest_authentication_status(self):
        return self.clientrequest_post(Endpoints.AuthenticationStatus.value)

    # Session->Reauthenticate = re-authenticate if valid session exists
    def clientrequest_reauthenticate(self):
        return self.clientrequest_post(Endpoints.Reauthenticate.value)

    # Session->Validate = validate current session
    def clientrequest_validate(self):
        return self.clientrequest_get(Endpoints.Validate.value)

    # Trades->Trades = Request to get trades from current and previous 6 days
    def clientrequest_trades(self):
        return self.clientrequest_get(Endpoints.Trades.value)

    # Account->BrokerageAccounts = Get list of accessible trading accounts
    def clientrequest_brokerage_accounts(self):
        return self.clientrequest_get(Endpoints.BrokerageAccounts.value)


if __name__ == '__main__':
    print("=== IB Client Portal API ===")
