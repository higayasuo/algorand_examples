# from conftest import client
from typing import Iterator

import pytest

from algosdk.v2client.algod import AlgodClient
from algosdk.error import AlgodHTTPError
from algosdk.logic import get_application_address
from algosdk.future.transaction import (
    AssetOptInTxn,
    ApplicationNoOpTxn,
    PaymentTxn,
    AssetTransferTxn,
)

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
    sign_send_wait_group_transactions,
)
from accounts import test1_address, test1_private_key, test2_private_key, test2_address
from escrow_asc1 import (
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


@pytest.fixture
def buy(
    client: AlgodClient,
    app_id: int,
    asset_id: int,
) -> Iterator[bool]:
    print("buy()")
    sp = client.suggested_params()

    txn1 = AssetOptInTxn(test2_address, sp, index=asset_id)
    txn2 = ApplicationNoOpTxn(
        test2_address,
        sp,
        app_id,
        app_args=[AppMethods.transfer_asset],
        foreign_assets=[asset_id],
        accounts=[test1_address],
    )
    txn3 = PaymentTxn(test2_address, sp, receiver=test1_address, amt=1000000)
    sign_send_wait_group_transactions(
        client,
        [txn1, txn2, txn3],
        [test2_private_key, test2_private_key, test2_private_key],
    )

    yield True

    print("undo buy()")
    sp = client.suggested_params()
    txn4 = PaymentTxn(test1_address, sp, receiver=test2_address, amt=1000000)
    txn5 = AssetTransferTxn(
        test2_address,
        sp,
        index=asset_id,
        receiver=test1_address,
        close_assets_to=test1_address,
        amt=0,
    )
    sign_send_wait_group_transactions(
        client,
        [txn4, txn5],
        [test1_private_key, test2_private_key],
    )


def test_escrow_asc1(
    client: AlgodClient, app_id: int, asset_id: int, opt_in: bool
) -> None:
    with pytest.raises(AlgodHTTPError) as e:
        call_app(
            client,
            test2_private_key,
            app_id,
            app_args=[AppMethods.transfer_asset],
            foreign_assets=[asset_id],
            accounts=[test1_address],
        )
    print(e)

    assert app_id > 0
    assert asset_id > 0
    assert opt_in


def test_escrow_asc1_2(
    client: AlgodClient, app_id: int, app_address: int, asset_id: int, opt_in: bool
) -> None:
    with pytest.raises(AlgodHTTPError) as e:
        fund(client, test1_private_key, app_address, 1000)
        call_app(
            client,
            test2_private_key,
            app_id,
            app_args=[AppMethods.transfer_asset],
            foreign_assets=[asset_id],
            accounts=[test1_address],
        )
    print(e)

    assert app_id > 0
    assert app_address
    assert asset_id > 0
    assert opt_in


def test_escrow_asc1_3(
    client: AlgodClient,
    app_id: int,
    app_address: int,
    asset_id: int,
    opt_in: bool,
    fund_to_app: bool,
) -> None:
    call_app(
        client,
        test2_private_key,
        app_id,
        app_args=[AppMethods.transfer_asset],
        foreign_assets=[asset_id],
        accounts=[test1_address],
    )

    assert app_id > 0
    assert app_address
    assert asset_id > 0
    assert opt_in
    assert fund_to_app


def test_escrow_asc1_4(
    fund_to_app: bool,
    buy: bool,
) -> None:
    assert fund_to_app
    assert buy
