from algosdk.v2client.algod import AlgodClient
from algosdk.account import address_from_private_key
from algosdk.future.transaction import (
    AssetTransferTxn,
)

import helper

from helper import (
    create_algod_client,
    sign_send_wait_transaction,
)
from accounts import test1_private_key, test1_address, test2_address, test2_private_key


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


def transfer_asset(
    client: AlgodClient,
    private_key: str,
    asset_sender: bytes | str,
    asset_receiver: bytes | str,
    asset_id: int,
) -> None:
    sender = address_from_private_key(private_key)
    params = client.suggested_params()

    txn = AssetTransferTxn(
        sender=sender,
        sp=params,
        receiver=asset_receiver,
        amt=1,
        index=asset_id,
        revocation_target=asset_sender,
    )
    sign_send_wait_transaction(client, txn, private_key)


def main():
    client = create_algod_client()

    asset_id = create_asset(client, test1_private_key, test2_address)
    transfer_asset(
        client,
        test2_private_key,
        asset_sender=test1_address,
        asset_receiver=test2_address,
        asset_id=asset_id,
    )


if __name__ == "__main__":
    main()
