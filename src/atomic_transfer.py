from algosdk.future.transaction import PaymentTxn, calculate_group_id

from helper import (
    create_algod_client,
    send_wait_transaction,
    sign_send_wait_group_transactions,
)
from accounts import (
    test1_address,
    test1_private_key,
    test2_address,
    test2_private_key,
)


def main():
    client = create_algod_client()
    params = client.suggested_params()

    tx1 = PaymentTxn(test1_address, params, test2_address, 1000)
    tx2 = PaymentTxn(test2_address, params, test1_address, 1000)

    gid = calculate_group_id([tx1, tx2])
    tx1.group = gid
    tx2.group = gid

    stx1 = tx1.sign(test1_private_key)
    stx2 = tx2.sign(test2_private_key)

    send_wait_transaction(client, [stx1, stx2])


def main2():
    client = create_algod_client()
    params = client.suggested_params()

    tx1 = PaymentTxn(test1_address, params, test2_address, 1000)
    tx2 = PaymentTxn(test2_address, params, test1_address, 1000)

    sign_send_wait_group_transactions(
        client, [tx1, tx2], [test1_private_key, test2_private_key]
    )


if __name__ == "__main__":
    main2()
