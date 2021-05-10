# clientportal_http.py

from overrides import overrides
from ib.endpoints import Endpoints
from ib.httpendpoints import HttpEndpoints
from ib.watchdog import Watchdog
from loguru import logger


class ClientPortalHttp(HttpEndpoints):
    # TODO: Document ClientPortalHttp class
    """
    Interactive Brokers ClientPortal Interface (HTTP).
    Refer to https://www.interactivebrokers.com/api/doc.html for API documentation
    Swagger can be used to test client requests: https://interactivebrokers.github.io/cpwebapi/swagger-ui.html
    Consult curl.trillworks.com for conversion of curl commands to Python requests
    """
    def __init__(self):
        super().__init__()
        self.name = 'HTTP'
        # Base used by all endpoints
        self.url_http = 'https://localhost:5000/v1/portal'
        logger.log('DEBUG', f'Clientportal (HTTP) Started with gateway: {self.url_http}')

    @overrides
    def watchdog_task(self):
        super().watchdog_task()
        result = self.clientrequest_ping()

    # TODO: Add logging wrappers
    def clientrequest_ping(self):
        """ Send session keep-alive."""
        return self.clientrequest_post(Endpoints.Ping.value)

    def clientrequest_authentication_status(self):
        """ Get current session status."""
        return self.clientrequest_post(Endpoints.AuthenticationStatus.value)

    def clientrequest_reauthenticate(self):
        """ Re-authenticate a session."""
        return self.clientrequest_post(Endpoints.Reauthenticate.value)

    def clientrequest_validate(self):
        """ Validate the current session."""
        return self.clientrequest_get(Endpoints.Validate.value)

    def clientrequest_trades(self):
        """ Return trades from last current and previous 6 days."""
        return self.clientrequest_get(Endpoints.Trades.value)

    def clientrequest_brokerage_accounts(self):
        """ Get list of accessible trading accounts."""
        return self.clientrequest_get(Endpoints.BrokerageAccounts.value)


if __name__ == '__main__':
    print("=== IB Client Portal (HTTP) ===")
