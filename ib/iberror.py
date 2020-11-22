# iberror.py
# Various error codes

from enum import Enum


class IBError(Enum):
    No_Error = 1
    Invalid_URL = 2


def testfunc(n):
    return n