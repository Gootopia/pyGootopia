# httpendpoints.py

import requests
import urllib3
from ib.error import Error
from ib.resultrequest import RequestResult
from lib.watchdog import Watchdog
from loguru import logger


class HttpEndpoints(Watchdog):
    # TODO: Document HttpEndpoints class
    """
    HttpEndpoints
    Provide Get/Post operations for a base URL with endpoints.
    """
    # used for JSON GET/POST requests
    headers = {'accept': 'application/json'}

    def __init__(self, name='Unknown', timeout_sec=5, autostart=True, disable_request_warnings=True):
        # kick off the watchdog
        super().__init__(name=name, timeout_sec=timeout_sec, autostart=autostart)

        # gateway base URL for submitting all client portal API. All commands append to this string
        self.url_http = ''
        self.request_timeout_sec = 10

        if disable_request_warnings:
            urllib3.disable_warnings()

    def clientrequest_get(self, endpoint=''):
        """ Gateway Get message request using desired endpoint. """
        cpurl, resp, exception = self.__get(endpoint)
        result = self.__error_check(cpurl, resp, exception)
        return result

    def clientrequest_post(self, endpoint=''):
        """ Gateway Post message request using desired endpoint."""
        cpurl, resp, exception = self.__post(endpoint)

        result = self.__error_check(cpurl, resp, exception)
        return result

    def __build_endpoint_url(self, endpoint: str = ''):
        url = self.url_http + endpoint
        return url

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
        except Exception as e:
            resp_exception = e
            pass

        # TODO: Refactor to use dataclass
        return cpurl, resp, resp_exception

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
        except Exception as e:
            resp_exception = e
            pass

        # TODO: Refactor to use dataclass
        return cpurl, resp, resp_exception

    @staticmethod
    def __error_check(cpurl, resp, exception):
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
            logger.log('DEBUG', f'{exception}')

        logger.log('DEBUG', f'{cpurl}: Error={result.error}, Status={result.statusCode}')
        return result


if __name__ == '__main__':
    print("=== HTTP Endpoint ===")
