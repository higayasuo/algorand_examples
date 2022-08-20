from typing import Iterator

import pytest

from algosdk.v2client.algod import AlgodClient
from algosdk.error import AlgodHTTPError
from algosdk.logic import get_application_address

import helper
from helper import (
    delete_app,
    destroy_asset,
    opt_in_asset,
    opt_out_asset,
    call_app,
    compile_smart_contract,
    create_app,
    fund,
)
from accounts import test1_address, test1_private_key, test2_private_key
from escrow_bad_asc1 import (
    approval_program,
    clear_state_program,
    global_schema,
    local_schema,
    AppMethods,
)


@pytest.fixture
def app_id(client: AlgodClient) -> Iterator[int]:
    approval = compile_smart_contract(client, approval_program())
    clear = compile_smart_contract(client, clear_state_program())

    id = create_app(
        client,
        test1_private_key,
        approval,
        clear,
        global_schema,
        local_schema,
    )
    yield id

    delete_app(client, test1_private_key, id)


@pytest.fixture
def app_address(app_id: int) -> str:
    address = get_application_address(app_id)
    print(f"Application Address: {address}")
    return address  # type:ignore[no-any-return]


@pytest.fixture
def asset_id(client: AlgodClient, app_address: str) -> Iterator[int]:
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
        clawback=app_address,
    )

    yield id

    destroy_asset(client, test1_private_key, id)


@pytest.fixture
def opt_in(client: AlgodClient, asset_id: int) -> Iterator[bool]:
    opt_in_asset(client, test2_private_key, asset_id)
    yield True
    opt_out_asset(
        client, test2_private_key, asset_id=asset_id, close_assets_to=test1_address
    )


@pytest.fixture
def fund_to_app(client: AlgodClient, app_address: str) -> bool:
    fund(client, test1_private_key, app_address, 101000)
    return True


def test_escrow_bad_asc1(
    client: AlgodClient,
    app_id: int,
    app_address: int,
    asset_id: int,
    opt_in: bool,
    fund_to_app: bool,
) -> None:
    with pytest.raises(AlgodHTTPError) as e:
        call_app(
            client,
            test2_private_key,
            app_id,
            # app_args=[AppMethods.transfer_asset],
            app_args=[AppMethods.transfer_asset, asset_id],
            # foreign_assets=[asset_id],
            accounts=[test1_address],
        )
    print(e)

    assert client
    assert app_id
    assert app_address
    assert asset_id
    assert opt_in
    assert fund_to_app
