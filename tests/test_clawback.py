# from conftest import client
from typing import Iterator

from algosdk.v2client.algod import AlgodClient
from algosdk.error import AlgodHTTPError

import pytest

import helper
from helper import (
    destroy_asset,
    transfer_asset,
    opt_in_asset,
    opt_out_asset,
    revoke_asset,
)
from accounts import test1_address, test1_private_key, test2_address, test2_private_key


@pytest.fixture
def asset_id(client: AlgodClient) -> Iterator[int]:

    id = helper.create_asset(
        client,
        test1_private_key,
        asset_name="ASA",
        unit_name="ASA",
        total=1,
        decimals=0,
        default_frozen=True,
        manager=test1_address,
        reserve=test1_address,
        freeze=test1_address,
        clawback=test2_address,
    )

    yield id

    destroy_asset(client, test1_private_key, id)


@pytest.fixture
def opt_in(client: AlgodClient, asset_id: int) -> Iterator[None]:
    opt_in_asset(client, test2_private_key, asset_id)
    yield
    opt_out_asset(
        client, test2_private_key, asset_id=asset_id, close_assets_to=test1_address
    )


def test_clawback(client: AlgodClient, asset_id: int) -> None:
    with pytest.raises(AlgodHTTPError) as e:
        transfer_asset(
            client, test1_private_key, receiver=test2_address, asset_id=asset_id
        )
    print(e)
    assert asset_id > 0


def test_clawback2(client: AlgodClient, asset_id: int, opt_in: None) -> None:
    with pytest.raises(AlgodHTTPError) as e:
        transfer_asset(
            client, test1_private_key, receiver=test2_address, asset_id=asset_id
        )
    print(e)
    assert asset_id > 0


def test_clawback3(client: AlgodClient, asset_id: int, opt_in: None) -> None:
    with pytest.raises(AlgodHTTPError) as e:
        transfer_asset(
            client, test2_private_key, receiver=test2_address, asset_id=asset_id
        )
    print(e)
    assert asset_id > 0


def test_clawback4(client: AlgodClient, asset_id: int, opt_in: None) -> None:
    revoke_asset(
        client,
        test2_private_key,
        receiver=test2_address,
        asset_id=asset_id,
        revocation_target=test1_address,
    )
    assert asset_id > 0
