from algosdk.v2client.algod import AlgodClient
from algosdk.account import address_from_private_key
from algosdk.logic import get_application_address
from algosdk.future.transaction import (
    ApplicationNoOpTxn,
    AssetOptInTxn,
    PaymentTxn,
    calculate_group_id,
)

from pyteal import compileTeal, Mode

import helper

from helper import (
    create_algod_client,
    compile_smart_contract,
    create_app,
    read_global_state,
    send_wait_transaction,
)
from accounts import test1_private_key, test2_private_key
import escrow_asc1


def create_asset(client: AlgodClient, private_key: str, escrow_address: str):
    sender = address_from_private_key(private_key)

    return helper.create_asset(
        client,
        private_key,
        total=1,
        decimals=0,
        default_frozen=True,
        unit_name="ASA",
        asset_name="ASA",
        manager=sender,
        reserve=sender,
        freeze=sender,
        clawback=escrow_address,
    )


def create_escrow_asc1(client: AlgodClient, private_key: str) -> tuple:
    approval_teal = compileTeal(
        escrow_asc1.approval_program(), Mode.Application, version=6
    )
    approval = compile_smart_contract(client, approval_teal)

    clear_teal = compileTeal(
        escrow_asc1.clear_state_program(), Mode.Application, version=6
    )
    clear = compile_smart_contract(client, clear_teal)

    app_id = create_app(
        client,
        private_key,
        approval,
        clear,
        escrow_asc1.global_schema,
        escrow_asc1.local_schema,
    )
    app_address = get_application_address(app_id)
    print("Application Address:", app_address)

    print(read_global_state(client, app_id))

    return app_id, app_address


def init_escrow_asc1(client: AlgodClient, private_key: str, app_id: int, asset_id: int):
    print("init_escrow_asc1")
    sender = address_from_private_key(private_key)
    params = client.suggested_params()

    amount = 1000000
    app_args = [escrow_asc1.AppMethods.init, amount]
    txn = ApplicationNoOpTxn(
        sender, params, app_id, app_args, foreign_assets=[asset_id]
    )
    # sign_send_wait_transaction(client, txn, private_key)

    app_address = get_application_address(app_id)
    txn2 = PaymentTxn(sender, params, app_address, 101000)
    # sign_send_wait_transaction(client, txn2, private_key)

    gid = calculate_group_id([txn, txn2])
    txn.group = gid
    txn2.group = gid
    stxn = txn.sign(private_key)
    stxn2 = txn2.sign(private_key)

    send_wait_transaction(client, [stxn, stxn2])
    print(read_global_state(client, app_id))


def buy(
    client: AlgodClient,
    private_key: str,
    app_id: int,
    asset_id: int,
    owner_address: str,
):
    print("buy")
    sender = address_from_private_key(private_key)
    params = client.suggested_params()

    txn = AssetOptInTxn(sender=sender, sp=params, index=asset_id)

    app_args = [escrow_asc1.AppMethods.buy]
    txn2 = ApplicationNoOpTxn(
        sender,
        params,
        app_id,
        app_args,
        foreign_assets=[asset_id],
        accounts=[owner_address],
    )

    gid = calculate_group_id([txn, txn2])
    txn.group = gid
    txn2.group = gid
    stxn = txn.sign(private_key)
    stxn2 = txn2.sign(private_key)
    send_wait_transaction(client, [stxn, stxn2])

    print(read_global_state(client, app_id))


def main():
    client = create_algod_client()
    owner_private_key = test1_private_key
    owner_address = address_from_private_key(owner_private_key)

    app_id, escrow_address = create_escrow_asc1(client, owner_private_key)
    asset_id = create_asset(client, owner_private_key, escrow_address)

    init_escrow_asc1(client, owner_private_key, app_id, asset_id)

    buyer_private_key = test2_private_key
    buy(client, buyer_private_key, app_id, asset_id, owner_address)


if __name__ == "__main__":
    main()
