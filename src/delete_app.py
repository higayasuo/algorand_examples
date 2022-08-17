import sys

from algosdk.future.transaction import (
    ApplicationDeleteTxn,
)

from helper import (
    create_algod_client,
    sign_send_wait_transaction,
)
from accounts import test1_private_key, test1_address


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/destroy_app.py app_id")
        sys.exit(1)

    client = create_algod_client()
    params = client.suggested_params()

    txn = ApplicationDeleteTxn(
        sender=test1_address,
        sp=params,
        index=int(sys.argv[1]),
    )
    sign_send_wait_transaction(client, txn, test1_private_key)


if __name__ == "__main__":
    main()
