from algosdk.v2client.algod import AlgodClient
from algosdk.account import address_from_private_key
from algosdk.future.transaction import (
    ApplicationNoOpTxn,
    PaymentTxn,
)
from algosdk.logic import get_application_address

import helper

from helper import (
    create_algod_client,
    delete_app,
    sign_send_wait_group_transactions,
    compile_smart_contract,
    create_app,
    read_global_state,
    destroy_asset,
)
from accounts import test1_private_key, test2_private_key
from escrow4_asc1 import (
    approval_program,
    clear_state_program,
    global_schema,
    local_schema,
    AppMethods,
)
from utils import print_red


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

    return helper.create_asset(  # type: ignore[no-any-return]
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


def init_app(
    client: AlgodClient,
    private_key: str,
    app_id: int,
    escrow_address: str,
    asset_id: int,
) -> None:
    print("init_app()")
    sender = address_from_private_key(private_key)
    params = client.suggested_params()

    price = 1000000
    txn1 = ApplicationNoOpTxn(
        sender,
        params,
        index=app_id,
        app_args=[AppMethods.init, price],
        foreign_assets=[asset_id],
    )
    txn2 = PaymentTxn(sender, params, receiver=escrow_address, amt=102000)
    sign_send_wait_group_transactions(client, [txn1, txn2], [private_key, private_key])

    print(read_global_state(client, app_id))


def main() -> None:
    client = create_algod_client()

    app_id, escrow_address = create_escrow_asc1(client, test1_private_key)
    asset_id = create_asset(client, test1_private_key, escrow_address)

    try:
        init_app(
            client,
            test2_private_key,
            app_id=app_id,
            escrow_address=escrow_address,
            asset_id=asset_id,
        )
    except Exception as e:
        print_red(f"Exception: {e}")
    finally:
        destroy_asset(client, test1_private_key, asset_id=asset_id)
        delete_app(client, test1_private_key, app_id=app_id)


if __name__ == "__main__":
    main()
