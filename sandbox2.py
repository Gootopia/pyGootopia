# sandbox2.py
from ib.ibclientportal import IbClientPortal


def main():
    cp = IbClientPortal()
    resp = cp.post(cp.Endpoints.Status)
    print(resp.json())
    print('done')


if __name__ == '__main__':
    main()
