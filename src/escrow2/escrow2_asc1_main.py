from algosdk.v2client.algod import AlgodClient
from algosdk.account import address_from_private_key
from algosdk.future.transaction import (
    AssetOptInTxn,
    ApplicationNoOpTxn,
    AssetTransferTxn,
    AssetDestroyTxn,
    ApplicationDeleteTxn,
    PaymentTxn,
)
from algosdk.logic import get_application_address

import helper

from helper import (
    create_algod_client,
    sign_send_wait_group_transactions,
    compile_smart_contract,
    create_app,
    read_global_state,
)
from accounts import test1_private_key, test1_address, test2_private_key
from escrow2_asc1 import (
    approval_program,
    clear_state_program,
    global_schema,
    local_schema,
    AppMethods,
)


def create_escrow_asc1(client: AlgodClient, private_key: str) -> tuple[int, str]:
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

    return helper.create_asset(  # type:ignore[no-any-return]
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


def init_app(
    client: AlgodClient,
    private_key: str,
    app_id: int,
    escrow_address: str,
    asset_id: int,
) -> None:
    print("init_app()")
    sender = address_from_private_key(private_key)
    sp = client.suggested_params()

    price = 1000000
    txn1 = ApplicationNoOpTxn(
        sender,
        sp,
        index=app_id,
        app_args=[AppMethods.init, price],
        foreign_assets=[asset_id],
    )
    txn2 = PaymentTxn(sender, sp, receiver=escrow_address, amt=102000)
    sign_send_wait_group_transactions(client, [txn1, txn2], [private_key, private_key])

    print(read_global_state(client, app_id))


def buy(
    client: AlgodClient,
    private_key: str,
    asset_sender: bytes | str,
    app_id: int,
    asset_id: int,
) -> None:
    print("buy()")
    sender = address_from_private_key(private_key)
    params = client.suggested_params()

    txn1 = AssetOptInTxn(sender=sender, sp=params, index=asset_id)
    app_args = [AppMethods.transfer_asset]
    txn2 = ApplicationNoOpTxn(
        sender,
        params,
        app_id,
        app_args,
        foreign_assets=[asset_id],
        accounts=[asset_sender],
    )
    txn3 = PaymentTxn(sender, params, receiver=asset_sender, amt=1000000)
    sign_send_wait_group_transactions(
        client, [txn1, txn2, txn3], [private_key, private_key, private_key]
    )


def reset(
    client: AlgodClient,
    seller_private_key: str,
    buyer_private_key: str,
    app_id: int,
    asset_id: int,
) -> None:
    print("reset()")
    seller = address_from_private_key(seller_private_key)
    buyer = address_from_private_key(buyer_private_key)
    sp = client.suggested_params()

    txn1 = ApplicationNoOpTxn(
        seller,
        sp,
        index=app_id,
        app_args=[AppMethods.transfer_asset],
        foreign_assets=[asset_id],
        accounts=[buyer],
    )
    txn2 = AssetTransferTxn(
        buyer,
        sp,
        index=asset_id,
        receiver=seller,
        close_assets_to=seller,
        amt=0,
    )
    txn3 = AssetDestroyTxn(seller, sp, index=asset_id)
    txn4 = ApplicationDeleteTxn(seller, sp, index=app_id)
    txn5 = PaymentTxn(seller, sp, receiver=buyer, amt=1000000)
    sign_send_wait_group_transactions(
        client,
        [txn1, txn2, txn3, txn4, txn5],
        [
            seller_private_key,
            buyer_private_key,
            seller_private_key,
            seller_private_key,
            seller_private_key,
        ],
    )


def main() -> None:
    client = create_algod_client()

    app_id, escrow_address = create_escrow_asc1(client, test1_private_key)
    asset_id = create_asset(client, test1_private_key, escrow_address)
    init_app(
        client,
        test1_private_key,
        app_id=app_id,
        escrow_address=escrow_address,
        asset_id=asset_id,
    )

    buy(
        client,
        test2_private_key,
        asset_sender=test1_address,
        app_id=app_id,
        asset_id=asset_id,
    )

    reset(
        client, test1_private_key, test2_private_key, app_id=app_id, asset_id=asset_id
    )


if __name__ == "__main__":
    main()
