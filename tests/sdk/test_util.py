from sdk.util import create_algod_client


def test_create_algod_client():
    assert create_algod_client() != None, 'algod_client is None'
