# ib_resultrequest.py
# Response message from IB client requests

from ib.iberror import IBError


class IBRequestResult:
    # Decoded message for error
    error: IBError = IBError.No_Error
    # Client portal Web Error Code
    statusCode = 0
    # Client Portal JSON string
    json: str = None
