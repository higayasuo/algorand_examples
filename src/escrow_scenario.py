from algosdk.v2client.algod import AlgodClient
from algosdk.logic import get_application_address

from pyteal import compileTeal, Mode

import helper

from helper import (create_algod_client,
                    sign_send_wait_transaction, compile_smart_contract, create_app,
                    read_global_state)
from accounts import test1_address, test1_private_key
import escrow_asc1


def create_asset(client: AlgodClient):
    sender = test1_address
    sender_private_key = test1_private_key

    return helper.create_asset(client, sender, sender_private_key,
                               total=1,
                               decimals=0,
                               default_frozen=True,
                               unit_name='TEST',
                               asset_name='ASA',
                               manager=sender,
                               reserve=sender,
                               freeze=sender,
                               clawback=sender,
                               )


def create_escrow_asc1(client: AlgodClient, asset_id: int) -> int:
    approval_teal = compileTeal(
        escrow_asc1.approval_program(), Mode.Application, version=6)
    approval = compile_smart_contract(client, approval_teal)

    clear_teal = compileTeal(
        escrow_asc1.clear_state_program(), Mode.Application, version=6)
    clear = compile_smart_contract(client, clear_teal)

    app_id = create_app(client, test1_private_key, approval,
                        clear, escrow_asc1.global_schema, escrow_asc1.local_schema,
                        foreign_assets=[asset_id])
    app_address = get_application_address(app_id)
    print('Application Address:', app_address)

    print(read_global_state(client, app_id))

    return app_id, app_address


def main():
    client = create_algod_client()
    asset_id = create_asset(client)
    app_id, app_address = create_escrow_asc1(client, asset_id)


if __name__ == '__main__':
    main()
