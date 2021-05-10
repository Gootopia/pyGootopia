# test_certificate.py
from lib.certificate import Certificate
from lib.certificate import CertificateError
from pathlib import Path
from unittest.mock import patch
import lib.certificate
import pytest


def test_get_certificate_bad_path():
    """ Fail when bad path/filename"""
    result = Certificate.get_certificate(certificate_path='notexist')

    assert result.ssl_context is None
    assert result.error is CertificateError.Invalid_Path


def test_get_certificate_not_valid():
    """ Fail when ssl doesn't like ssl_context """
    # The private test key should cause an "X509: NO_CERTIFICATE_OR_CRL_FOUND" error via ssl.SSLERROR exception
    local_test_path = Path(__file__).with_name('test_private_key.pem')
    result = Certificate.get_certificate(certificate_path=local_test_path)

    assert result.ssl_context is None
    assert result.error is CertificateError.Invalid_Certificate


def test_get_certificate_happy():
    """ Happy Path test"""
    local_test_path = Path(__file__).with_name('test_public_key.pem')
    result = Certificate.get_certificate(certificate_path=local_test_path)

    assert result.ssl_context is not None
    assert result.error is CertificateError.Ok