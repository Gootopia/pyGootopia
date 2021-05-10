# ssl_context.py
import ssl
from enum import Enum
from pathlib import Path
from dataclasses import dataclass


class CertificateError(Enum):
    Ok = 0,
    Invalid_Path = 1    # path is wrong or filename is bad
    Invalid_Certificate = 2    # ssl library doesn't consider file a good ssl_context


@dataclass
class CertificateReturn:
    ssl_context: ssl.SSLContext
    error: CertificateError


class Certificate:
    """ Instructions on how to make a ssl_context
    See: https://talkdotnet.wordpress.com/2019/08/07/generating-a-pem-private-and-public-certificate-with-openssl-on-windows/
    Perform the following in the same directory as this .py module
    1) openssl req -x509 -newkey rsa:4096 -keyout {keyname}.pem -out {publickey_name}.pem -nodes
    2) openssl x509 -outform der -in {publickey_name}.pem -out {publickey_name}.crt
    """
    @staticmethod
    def get_certificate(certificate_path='') -> CertificateReturn:
        """ Obtain a ssl_context for use in SSL operations."""

        result = CertificateReturn(None, CertificateError.Ok)

        if Path(certificate_path).exists() is not True:
            result.error = CertificateError.Invalid_Path
            return result

        try:
            result.ssl_context = ssl.SSLContext(ssl.CERT_REQUIRED)
            result.ssl_context.load_verify_locations(certificate_path)
        except ssl.SSLError as e:
            result.ssl_context = None
            result.error = CertificateError.Invalid_Certificate
            pass
        finally:
            return result
