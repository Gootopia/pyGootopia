# ib_endpoints.py
# Interactive Brokers Client Portal Web API endpoints
# See: https://www.interactivebrokers.com/api/doc.html
from enum import Enum


class IBEndpoints(Enum):
    Blank = ''
    Status = '/iserver/auth/status'
    Trades = '/iserver/account/trades'