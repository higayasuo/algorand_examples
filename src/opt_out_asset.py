import sys

from helper import opt_out_asset

from helper import (
    create_algod_client,
)
from accounts import test1_address, test2_private_key


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/opt_out_asset.py asset_id")
        sys.exit(1)

    client = create_algod_client()

    opt_out_asset(
        client,
        test2_private_key,
        close_assets_to=test1_address,
        asset_id=int(sys.argv[1]),
    )


if __name__ == "__main__":
    main()
