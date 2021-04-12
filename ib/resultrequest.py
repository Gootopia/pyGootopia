# resultrequest.py
# Response message from IB client requests

from ib.error import Error


class RequestResult:
    # Decoded message for error
    error: Error = Error.No_Error
    # Client portal Web Error Code
    statusCode = 0
    # Client Portal JSON string
    json: str = None
