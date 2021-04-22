# ibclientport.py
# IB Client Portal for REST requests
# Refer to https://www.interactivebrokers.com/api/doc.html for API documentation
# Swagger can be used to test client requests: https://interactivebrokers.github.io/cpwebapi/swagger-ui.html
# Consult curl.trillworks.com for conversion of curl commands to Python requests
import requests
import time
from threading import Thread
from ib.error import Error
from ib.endpoints import Endpoints
from ib.resultrequest import RequestResult


class ClientPortal(Thread):
    # used for ib client portal JSON GET/POST requests
    headers = {'accept': 'application/json'}

    # request timeout (seconds)
    request_timeout = 10

    # watchdog ping timer (second)
    watchdog_timeout = 30

    # base URL for submitting all client portal API. All commands append to this string
    # Note that the last backslash is omitted so that we match the IB docs
    apiUrlBase = "https://localhost:5000/v1/portal"

    # constructor
    def __init__(self):
        # start a background thread that periodically pings the IB gateway to keep it alive
        Thread.__init__(self)
        self.daemon = True
        self.start()
        pass

    # Thread execution task. Background watchdog task for ibclient.
    # Call "kill_watchdog" or manually set timeout to 0 to terminate
    def run(self):
        while True:
            print(self.watchdog_timeout)
            if self.watchdog_timeout >= 1:
                resp = self.clientrequest_ping()
                time.sleep(self.watchdog_timeout)
            else:
                print("==== WATCHDOG KILLED ====")
                break

    # manually set the timeout to 0 to kill the watchdog process on its next pass.
    # TODO: Kill process immediately
    def kill_watchdog(self):
        self.watchdog_timeout = 0
        print(self.watchdog_timeout)

    # Session->Ping = Ping the server to keep session open
    @classmethod
    def clientrequest_ping(cls):
        return cls.__clientrequest_post(Endpoints.Ping)

    # Session->Authentication Status = Request to get client status
    @classmethod
    def clientrequest_authentication_status(cls):
        return cls.__clientrequest_post(Endpoints.AuthenticationStatus)

    # Session->Reauthenticate = re-authenticate if valid session exists
    @classmethod
    def clientrequest_reauthenticate(cls):
        return cls.__clientrequest_post(Endpoints.Reauthenticate)

    # Session->Validate = validate current session
    @classmethod
    def clientrequest_validate(cls):
        return cls.__clientrequest_get(Endpoints.Validate)

    # Trades->Trades = Request to get trades from current and previous 6 days
    @classmethod
    def clientrequest_trades(cls):
        return cls.__clientrequest_get(Endpoints.Trades)

    # Account->BrokerageAccounts = Get list of accessible trading accounts
    @classmethod
    def clientrequest_brokerage_accounts(cls):
        return cls.__clientrequest_get(Endpoints.BrokerageAccounts)

    # Manual generic client Get request.
    @classmethod
    def __clientrequest_get(cls, endpoint: Endpoints):
        resp, exception = cls.__get(endpoint)
        result = cls.__error_check(resp, exception)
        return result

    # Manual generic client Post request.
    @classmethod
    def __clientrequest_post(cls, endpoint: Endpoints):
        resp, exception = cls.__post(endpoint)
        result = cls.__error_check(resp, exception)
        return result

    # URL string builder. Separate function so it's testable
    @staticmethod
    def __build_endpoint_url(endpoint: Endpoints):
        url = ClientPortal.apiUrlBase + endpoint.value
        return url

    # submit GET request to portal API
    @classmethod
    def __get(cls, endpoint: Endpoints):
        cpurl = cls.__build_endpoint_url(endpoint)
        print(f'Portal: {cpurl}')
        resp = None
        resp_exception = None
        # Without verify=False, we get issues with untrusted SSL certificates
        # This should be ok for demo accounts, but need to follow up on this for live accounts
        # See https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        # resp is the web response. Use resp.json() to get the client request specific response
        # resp = requests.post(cpurl, headers=self.headers, json=data, verify=False)
        try:
            resp = requests.get(cpurl, headers=cls.headers, verify=False, timeout=cls.request_timeout)

        # grab any exceptions and return. They will be passed off to __error_check for handling
        except Exception as resp_exception:
            pass

        return resp, resp_exception

    # submit POST request to portal API
    @classmethod
    def __post(cls, endpoint: Endpoints, data: str = ''):
        cpurl = cls.__build_endpoint_url(endpoint)
        print(f'Portal: {cpurl}')
        resp = None
        resp_exception = None
        # Without verify=False, we get issues with untrusted SSL certificates
        # This should be ok for demo accounts, but need to follow up on this for live accounts
        # See https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        # resp is the web response. Use resp.json() to get the client request specific response
        try:
            resp = requests.post(cpurl, headers=cls.headers, json=data, verify=False, timeout=cls.request_timeout)

        # grab any exceptions and return. They will be passed off to __error_check for handling
        except Exception as resp_exception:
            pass

        return resp, resp_exception

    # Generic error checking needed for all portal requests.
    @staticmethod
    def __error_check(resp, exception):
        result = RequestResult()

        # resp will be None if we had an exception
        if resp is not None:
            # If Ok = False, there was a problem submitting the request, typically an invalid URL
            if not resp.ok:
                result.error = Error.Invalid_URL
            else:
                # conversion to give the request specific json results
                result.json = resp.json()
                result.statusCode = resp.status_code
        else:
            result.error = Error.Connection_or_Timeout
            print(exception)

        return result


if __name__ == '__main__':
    print("=== IB Client Portal API ===")
