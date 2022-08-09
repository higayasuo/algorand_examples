from algosdk.v2client.algod import AlgodClient
from algosdk.account import address_from_private_key
from algosdk.future.transaction import (
    AssetTransferTxn,
    AssetOptInTxn,
    AssetDestroyTxn,
    ApplicationNoOpTxn,
    ApplicationDeleteTxn,
    PaymentTxn,
)
from algosdk.logic import get_application_address
from algosdk.encoding import decode_address

from pyteal import compileTeal, Mode

import helper

from helper import (
    create_algod_client,
    sign_send_wait_group_transactions,
    compile_smart_contract,
    create_app,
    sign_send_wait_transaction,
)
from accounts import test1_private_key, test1_address, test2_private_key
import escrow_bad2_asc1 as escrow_asc1


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

    return app_id, app_address


def fund(
    client: AlgodClient, private_key: str, receiver: str | bytes, amt: int
) -> None:
    print("fund")
    sender = address_from_private_key(private_key)
    params = client.suggested_params()

    txn = PaymentTxn(sender, params, receiver=receiver, amt=amt)
    sign_send_wait_transaction(client, txn, private_key)


def create_asset(client: AlgodClient, private_key: str, clawback: str):
    sender = address_from_private_key(private_key)

    return helper.create_asset(
        client,
        private_key,
        total=1,
        decimals=0,
        default_frozen=False,
        unit_name="ASA",
        asset_name="ASA",
        manager=sender,
        reserve=sender,
        freeze=sender,
        clawback=clawback,
    )


def opt_in_transfer_asset_fund(
    client: AlgodClient,
    private_key: str,
    asset_sender: bytes | str,
    app_id: int,
    asset_id: int,
) -> None:
    print("opt_in_transfer_asset_fund")
    sender = address_from_private_key(private_key)
    params = client.suggested_params()

    txn1 = AssetOptInTxn(sender=sender, sp=params, index=asset_id)
    app_args = [escrow_asc1.AppMethods.transfer_asset, decode_address(asset_sender)]
    txn2 = ApplicationNoOpTxn(
        sender,
        params,
        app_id,
        app_args,
        foreign_assets=[asset_id],
    )
    txn3 = PaymentTxn(sender, params, receiver=asset_sender, amt=1000000)
    sign_send_wait_group_transactions(
        client, [txn1, txn2, txn3], [private_key, private_key, private_key]
    )


def return_destroy_asset_refund_delete_app(
    client: AlgodClient,
    sender_private_key: str,
    destroyer_private_key: str,
    asset_id: int,
    app_id: int,
) -> None:
    print("return_destroy_asset_refund_delete_app")
    sender = address_from_private_key(sender_private_key)
    destroyer = address_from_private_key(destroyer_private_key)
    params = client.suggested_params()

    txn1 = AssetTransferTxn(
        sender=sender,
        sp=params,
        receiver=destroyer,
        amt=1,
        index=asset_id,
        close_assets_to=destroyer,
    )
    txn2 = AssetDestroyTxn(
        sender=destroyer,
        sp=params,
        index=asset_id,
    )
    txn3 = PaymentTxn(destroyer, params, receiver=sender, amt=1000000)
    txn4 = ApplicationDeleteTxn(
        sender=destroyer,
        sp=params,
        index=app_id,
    )
    sign_send_wait_group_transactions(
        client,
        [txn1, txn2, txn3, txn4],
        [
            sender_private_key,
            destroyer_private_key,
            destroyer_private_key,
            destroyer_private_key,
        ],
    )


def main():
    client = create_algod_client()

    app_id, escrow_address = create_escrow_asc1(client, test1_private_key)
    fund(client, test1_private_key, receiver=escrow_address, amt=101000)
    asset_id = create_asset(client, test1_private_key, escrow_address)

    opt_in_transfer_asset_fund(
        client,
        test2_private_key,
        asset_sender=test1_address,
        app_id=app_id,
        asset_id=asset_id,
    )

    return_destroy_asset_refund_delete_app(
        client,
        sender_private_key=test2_private_key,
        destroyer_private_key=test1_private_key,
        asset_id=asset_id,
        app_id=app_id,
    )


if __name__ == "__main__":
    main()
