from algosdk.v2client.algod import AlgodClient
from algosdk.account import address_from_private_key
from algosdk.future.transaction import AssetTransferTxn, AssetOptInTxn, AssetDestroyTxn

import helper

from helper import (
    create_algod_client,
    sign_send_wait_group_transactions,
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


def opt_in_transfer_asset(
    client: AlgodClient,
    private_key: str,
    asset_sender: bytes | str,
    asset_receiver: bytes | str,
    asset_id: int,
) -> None:
    print("opt_in_transfer_asset")
    sender = address_from_private_key(private_key)
    params = client.suggested_params()

    txn1 = AssetOptInTxn(sender=sender, sp=params, index=asset_id)
    txn2 = AssetTransferTxn(
        sender=sender,
        sp=params,
        receiver=asset_receiver,
        amt=1,
        index=asset_id,
        revocation_target=asset_sender,
    )
    sign_send_wait_group_transactions(client, [txn1, txn2], [private_key, private_key])


def return_destroy_asset(
    client: AlgodClient,
    sender_private_key: str,
    destroyer_private_key: str,
    asset_id: int,
) -> None:
    print("return_destroy_asset")
    sender = address_from_private_key(sender_private_key)
    destroyer = address_from_private_key(destroyer_private_key)
    params = client.suggested_params()

    txn1 = AssetTransferTxn(
        sender=sender,
        sp=params,
        receiver=destroyer,
        amt=1,
        index=asset_id,
    )
    txn2 = AssetDestroyTxn(
        sender=destroyer,
        sp=params,
        index=asset_id,
    )
    sign_send_wait_group_transactions(
        client, [txn1, txn2], [sender_private_key, destroyer_private_key]
    )


def main():
    client = create_algod_client()

    asset_id = create_asset(client, test1_private_key, test2_address)
    opt_in_transfer_asset(
        client,
        test2_private_key,
        asset_sender=test1_address,
        asset_receiver=test2_address,
        asset_id=asset_id,
    )
    return_destroy_asset(
        client,
        sender_private_key=test2_private_key,
        destroyer_private_key=test1_private_key,
        asset_id=asset_id,
    )


if __name__ == "__main__":
    main()
