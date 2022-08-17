from algosdk.v2client.algod import AlgodClient
from algosdk.account import address_from_private_key

import helper
from helper import (
    create_algod_client,
    transfer_asset,
    opt_in_asset,
    destroy_asset,
)
from accounts import test1_private_key, test2_address, test2_private_key
from utils import print_red


def create_asset(client: AlgodClient, private_key: str, clawback: str) -> int:
    sender = address_from_private_key(private_key)

    return helper.create_asset(  # type: ignore[no-any-return]
        client,
        private_key,
        asset_name="ASA",
        unit_name="ASA",
        total=1,
        decimals=0,
        default_frozen=True,
        manager=sender,
        reserve=sender,
        freeze=sender,
        clawback=clawback,
    )


def main() -> None:
    client = create_algod_client()

    asset_id = create_asset(client, test1_private_key, test2_address)
    opt_in_asset(client, test2_private_key, asset_id)

    try:
        transfer_asset(
            client,
            test1_private_key,
            receiver=test2_address,
            asset_id=asset_id,
        )
    except Exception as e:
        print_red(f"Exception: {e}")
    finally:
        destroy_asset(client, test1_private_key, asset_id=asset_id)


if __name__ == "__main__":
    main()
