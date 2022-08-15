from algosdk.v2client.algod import AlgodClient
from algosdk.account import address_from_private_key
from algosdk.logic import get_application_address
from algosdk.future.transaction import PaymentTxn, AssetOptInTxn, ApplicationNoOpTxn

import helper

from helper import (
    create_algod_client,
    compile_smart_contract,
    create_app,
    delete_app,
    opt_in_asset,
    opt_out_asset,
    destroy_asset,
    call_app,
    fund,
    sign_send_wait_group_transactions,
)
from accounts import test1_private_key, test1_address, test2_private_key, test2_address
from escrow_asc1 import (
    approval_program,
    clear_state_program,
    global_schema,
    local_schema,
    AppMethods,
)


def create_escrow_asc1(client: AlgodClient, private_key: str) -> tuple:
    approval = compile_smart_contract(client, approval_program())
    clear = compile_smart_contract(client, clear_state_program())

    app_id = create_app(
        client,
        private_key,
        approval,
        clear,
        global_schema,
        local_schema,
    )
    app_address = get_application_address(app_id)
    print("Application Address:", app_address)

    return app_id, app_address


def create_asset(client: AlgodClient, private_key: str, clawback: str) -> int:
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
        clawback=clawback,
    )


def buy(
    client: AlgodClient,
    private_key: str,
    asset_sender: str,
    app_id: int,
    asset_id: int,
) -> None:
    print("buy()")
    sender = address_from_private_key(private_key)
    params = client.suggested_params()

    txn1 = AssetOptInTxn(sender=sender, sp=params, index=asset_id)
    txn2 = ApplicationNoOpTxn(
        sender,
        params,
        app_id,
        app_args=[AppMethods.transfer_asset],
        foreign_assets=[asset_id],
        accounts=[asset_sender],
    )
    txn3 = PaymentTxn(sender, params, receiver=asset_sender, amt=1000000)
    sign_send_wait_group_transactions(
        client, [txn1, txn2, txn3], [private_key, private_key, private_key]
    )


def main():
    client = create_algod_client()

    app_id, escrow_address = create_escrow_asc1(client, test1_private_key)
    asset_id = create_asset(client, test1_private_key, escrow_address)
    fund(client, test1_private_key, receiver=escrow_address, amt=102000)

    buy(
        client,
        test2_private_key,
        asset_sender=test1_address,
        app_id=app_id,
        asset_id=asset_id,
    )

    call_app(
        client,
        test1_private_key,
        app_id,
        app_args=[AppMethods.transfer_asset],
        foreign_assets=[asset_id],
        accounts=[test2_address],
    )
    opt_out_asset(
        client, test2_private_key, asset_id=asset_id, close_assets_to=test1_address
    )
    destroy_asset(client, test1_private_key, asset_id)
    delete_app(client, test1_private_key, app_id)
    fund(client, test1_private_key, receiver=test2_address, amt=1000000)


if __name__ == "__main__":
    main()
