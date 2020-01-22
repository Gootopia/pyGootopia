# iberr.py
# List of client portal errors
from enum import Enum


# Error class for errors
class IBError(Enum):
    ErrNone = 0
    Invalid_URL = -1  # Issue with the URL string.
    Endpoint_Not_Supported = -2 # Endpoint not yet implemented

