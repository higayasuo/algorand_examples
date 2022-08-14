from algosdk.v2client.algod import AlgodClient
from algosdk.account import address_from_private_key

import helper
from helper import create_algod_client, transfer_asset
from accounts import test1_private_key, test2_address


def create_asset(client: AlgodClient, private_key: str, clawback: str):
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


def main():
    client = create_algod_client()

    asset_id = create_asset(client, test1_private_key, test2_address)
    transfer_asset(
        client,
        test1_private_key,
        receiver=test2_address,
        asset_id=asset_id,
    )


if __name__ == "__main__":
    main()
