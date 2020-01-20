from pyIB.ib.ibcphttp import ibcphttp
from pyIB.ib.iberr import IBError


def main():
    cp=ibcphttp()
    resp = cp.post(cp.Endpoints.Status)
    print(resp.json())
    print('done')


if __name__ == '__main__':
    main()
