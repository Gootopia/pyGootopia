# ibclientport.py
# IB Client Portal for REST requests
# Refer to https://www.interactivebrokers.com/api/doc.html for API documentation
# Swagger can be used to test client requests: https://interactivebrokers.github.io/cpwebapi/swagger-ui.html
# Consult curl.trillworks.com for conversion of curl commands to Python requests
import requests
import os
import subprocess
from ib.iberror import IBError
from ib.ib_endpoints import IBEndpoints


class IBClientPortal:
    # used for ib client portal JSON GET/POST requests
    headers = {'accept': 'application/json'}

    # base URL for submitting all client portal API. All commands append to this string
    # Note that the last backslash is omitted so that we match the IB docs
    apiUrlBase = "https://localhost:5000/v1/portal"

    # Results of endpoint requests
    class RequestResult:
        # Decoded message for error
        error: IBError
        # Client portal Web Error Code
        statusCode: int
        # Client Portal JSON string
        json: str

    # constructor
    def __init__(self):
        pass

    # Request to get client status
    @classmethod
    def clientrequest_status(cls):
        return cls.clientrequest_generic_post(IBEndpoints.Status)

    # Request to get trades from current and previous 6 days
    @classmethod
    def clientrequest_trades(cls):
        return cls.clientrequest_generic_get(IBEndpoints.Trades)

    # generic client request. Call others for more specific responses and information output
    @classmethod
    def clientrequest_generic_get(cls, endpoint: IBEndpoints):
        resp = cls.__get(endpoint)
        result = cls.__error_check(resp, )
        return result

    # generic client request. Call others for more specific responses and information output
    @classmethod
    def clientrequest_generic_post(cls, endpoint: IBEndpoints):
        resp = cls.__post(endpoint)

        result = cls.__error_check(resp)
        return result

    # URL string builder. Separate function so it's testable
    @staticmethod
    def __build_endpoint_url(endpoint: IBEndpoints):
        url = IBClientPortal.apiUrlBase + endpoint.value
        return url

    # submit GET request to portal API
    @classmethod
    def __get(cls, endpoint: IBEndpoints):
        cpurl = cls.__build_endpoint_url(endpoint)
        print(f'Portal: {cpurl}')
        resp = None
        # Without verify=False, we get issues with untrusted SSL certificates
        # This should be ok for demo accounts, but need to follow up on this for live accounts
        # See https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        # resp is the web response. Use resp.json() to get the client request specific response
        # resp = requests.post(cpurl, headers=self.headers, json=data, verify=False)
        try:
            resp = requests.get(cpurl, headers=cls.headers, verify=False)

        except requests.exceptions.ConnectionError as e:
            print("==== GATEWAY NOT STARTED! ====")

        return resp

    # submit POST request to portal API
    @classmethod
    def __post(cls, endpoint: IBEndpoints, data: str = ''):
        cpurl = cls.__build_endpoint_url(endpoint)
        print(f'Portal: {cpurl}')
        resp = None
        # Without verify=False, we get issues with untrusted SSL certificates
        # This should be ok for demo accounts, but need to follow up on this for live accounts
        # See https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        # resp is the web response. Use resp.json() to get the client request specific response
        try:
            resp = requests.post(cpurl, headers=cls.headers, json=data, verify=False)

        except requests.exceptions.ConnectionError as e:
            print("==== GATEWAY NOT STARTED! ====")

        return resp

    # Generic error checking needed for all portal requests. Should call this after each function
    @staticmethod
    def __error_check(resp):
        error = IBError.No_Error

        # If Ok = False, there was a problem submitting the request
        if not resp.ok:
            error = IBError.Invalid_URL
            json = None
        else:
            # conversion to give the request specific json results
            json = resp.json()

        result = IBClientPortal.RequestResult()
        result.error = error
        result.statusCode = resp.status_code
        result.json = json
        return result


# region Client Portal Methods

# endregion Methods

if __name__ == '__main__':
    print("=== IB Client Portal API ===")
