# ibcphttp.py
# IB Client Portal
# Refer to https://www.interactivebrokers.com/api/doc.html for API documentation
# Swagger can be used to test client requests: https://interactivebrokers.github.io/cpwebapi/swagger-ui.html
# Consult curl.trillworks.com for conversion of curl commands to Python requests
import requests
from .iberr import IBError
from enum import Enum

class ibcphttp:
    # used for ib client portal JSON GET/POST requests
    headers = {'accept': 'application/json'}

    # base URL for submitting all client portal API. All commands append to this string
    # Note that the last backslash is ommitted so that we match the IB docs
    apiUrlBase = "https://localhost:5000/v1/portal"

    class RequestResult:
        error:IBError
        json:str

    # Supported endpoints. See IB API docs
    class Endpoints(Enum):
        Blank = ''
        Status = '/iserver/auth/status'
        Trades = '/iserver/account/trades'

    # constructor
    def __init__(self):
        pass

    # URL string builder. Separate function so it's testable
    @staticmethod
    def buildEndpointURL(self, endpoint:Endpoints):
        url= ibcphttp.apiUrlBase+endpoint.value
        return url

    # Request to get client status
    def clientRequest_Status(self):
        return self.clientRequest_GenericPost(ibcphttp.Endpoints.Status)

    # Request to get trades from current and previous 6 days
    def clientRequest_Trades(self):
        return self.clientRequest_GenericGet(ibcphttp.Endpoints.Trades)

    # generic client request. Call others for more specific responses and information output
    def clientRequest_GenericGet(self,endpoint:Endpoints):
        resp = self.__get__(endpoint)
        result = self.__errorCheck__(resp)
        return result

    # generic client request. Call others for more specific responses and information output
    def clientRequest_GenericPost(self,endpoint:Endpoints):
        resp = self.__post__(endpoint)
        result = self.__errorCheck__(resp)
        return result

    # submit GET request to portal API
    def __get__(self, endpoint : Endpoints, data: str =''):
        cpurl = self.buildEndpointURL(self, endpoint)
        print(f'Portal: {cpurl}')
        # Without verify=False, we get issues with untrusted SSL certificates
        # This should be ok for demo accounts, but need to follow up on this for live accounts
        # See https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        # resp is the web response. Use resp.json() to get the client request specific response
        #resp = requests.post(cpurl, headers=self.headers, json=data, verify=False)
        resp = requests.get(cpurl, headers=self.headers, verify=False)
        return resp

    # submit POST request to portal API
    def __post__(self, endpoint : Endpoints, data: str =''):
        cpurl = self.buildEndpointURL(self, endpoint)
        print(f'Portal: {cpurl}')
        # Without verify=False, we get issues with untrusted SSL certificates
        # This should be ok for demo accounts, but need to follow up on this for live accounts
        # See https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        # resp is the web response. Use resp.json() to get the client request specific response
        resp = requests.post(cpurl, headers=self.headers, json=data, verify=False)
        return resp

    # Generic error checking needed for all portal requests. Should call this after each function
    def __errorCheck__(self, resp):
        error = IBError.ErrNone

        # If Ok = False, there was a problem submitting the request
        if not resp.ok:
            error = IBError.Invalid_URL
            json = None
        else:
            # conversion to give the request specific json results
            json = resp.json()

        result = ibcphttp.RequestResult()
        result.error = error
        result.json = json
        return result

#region Client Portal Methods

# endregion Methods

if __name__ == '__main__':
    print("=== IB Client Portal API ===")
