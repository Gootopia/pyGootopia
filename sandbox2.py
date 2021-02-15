# sandbox2.py
# Sandbox for testing various client functions
from ib.ibclientportal import IBClientPortal


def main():
    resp = IBClientPortal.clientrequest_status()
    print(resp.statusCode)
    print(resp.json)
    print('done')


if __name__ == '__main__':
    main()
