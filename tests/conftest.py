import pytest

from algosdk.v2client.algod import AlgodClient

from helper import create_algod_client


@pytest.fixture(scope="session")
def client() -> AlgodClient:
    return create_algod_client()
