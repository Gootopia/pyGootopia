import unittest
from ib.ibclientportal import ibcphttp


class test_ibcphttp(unittest.TestCase):
    # Make sure base string for client portal is correct
    def test_apiUrlBase(self):
        self.assertEqual(ibcphttp.apiUrlBase, 'https://localhost:5000/v1/portal', 'Client base url incorrect')

    def test_buildEndpointBaseString(self):
        # check with blank string just to make sure the base string format is correct
        url = ibcphttp.build_endpoint_url(self, ibcphttp.Endpoints.Blank)
        self.assertEqual(url, ibcphttp.apiUrlBase, 'Incorrect base url format')

    def test_statusEndpointString(self):
        self.assertEqual(ibcphttp.Endpoints.Status.value, '/iserver/auth/status', 'Status endpoint incorrect')

    def test_tradesEndpointString(self):
        self.assertEqual(ibcphttp.Endpoints.Trades.value, '/iserver/account/trades', 'Trades endpoint incorrect')


if __name__ == '__main__':
    unittest.main()
