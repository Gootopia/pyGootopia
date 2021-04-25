# httpendpoints.py
# base for submitting get and put requests to an http client with endpoints
# Consult curl.trillworks.com for conversion of curl commands to Python requests
import requests
import urllib3
from ib.error import Error
from ib.resultrequest import RequestResult
from ib.watchdog import Watchdog


class HttpEndpoints(Watchdog):
    # used for JSON GET/POST requests
    headers = {'accept': 'application/json'}

    # constructor
    def __init__(self, disable_request_warnings=True):
        super().__init__()
        self.watchdog_timeout_sec = 10
        # gateway base URL for submitting all client portal API. All commands append to this string
        self.apiUrlBase = ''
        self.request_timeout_sec = 10

        # TODO: This gets rid of annoying security warnings for requests library. Need to figure out certificate stuff.
        if disable_request_warnings:
            urllib3.disable_warnings()

    def clientrequest_get(self, endpoint=''):
        resp, exception = self.__get(endpoint)
        result = self.__error_check(resp, exception)
        return result

    def clientrequest_post(self, endpoint=''):
        resp, exception = self.__post(endpoint)
        result = self.__error_check(resp, exception)
        return result

    def __build_endpoint_url(self, endpoint: str = ''):
        url = self.apiUrlBase + endpoint
        print(f'Portal: {url}')
        return url

    # submit GET request to portal API
    def __get(self, endpoint: str = ''):
        cpurl = self.__build_endpoint_url(endpoint)
        resp = None
        resp_exception = None
        # Without verify=False, we get issues with untrusted SSL certificates
        # This should be ok for demo accounts, but need to follow up on this for live accounts
        # See https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        # resp is the web response. Use resp.json() to get the client request specific response
        # resp = requests.post(cpurl, headers=self.headers, json=data, verify=False)
        try:
            resp = requests.get(cpurl, headers=HttpEndpoints.headers, verify=False, timeout=self.request_timeout_sec)

        # grab any exceptions and return. They will be passed off to __error_check for handling
        except Exception as resp_exception:
            pass

        return resp, resp_exception

    # submit POST request to portal API
    def __post(self, endpoint: str = '', data: str = ''):
        cpurl = self.__build_endpoint_url(endpoint)
        resp = None
        resp_exception = None
        # Without verify=False, we get issues with untrusted SSL certificates
        # This should be ok for demo accounts, but need to follow up on this for live accounts
        # See https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        # resp is the web response. Use resp.json() to get the client request specific response
        try:
            resp = requests.post(cpurl, headers=HttpEndpoints.headers,
                                 json=data, verify=False, timeout=self.request_timeout_sec)

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
    print("=== HTTP Endpoint ===")
