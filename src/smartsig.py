import base64
from calendar import c

from algosdk.future import transaction
from algosdk import mnemonic
from algosdk.v2client import algod
from pyteal import Int, And, Txn, TxnType, Global, Addr, compileTeal, Mode

from helper import compile_smart_signature, create_algod_client, sign_send_wait_transaction, send_wait_transaction


def donation_escrow(receiver_address):
    program = And(
        Txn.type_enum() == TxnType.Payment,
        Txn.fee() <= Int(1000),
        Txn.receiver() == Addr(receiver_address),
        Global.group_size() == Int(1),
        Txn.rekey_to() == Global.zero_address()
    )

    return compileTeal(program, Mode.Signature, version=6)


def payment_transaction(client, sender_mnemonic, receiver_address, amount):
    params = client.suggested_params()
    sender_address = mnemonic.to_public_key(sender_mnemonic)
    sender_private_key = mnemonic.to_private_key(sender_mnemonic)

    txn = transaction.PaymentTxn(
        sender_address, params, receiver_address, amount)
    sign_send_wait_transaction(client, txn, sender_private_key)


def lsig_payment_transaction(client, escrow_program, escrow_address, receiver_address, amount):
    params = client.suggested_params()
    txn = transaction.PaymentTxn(
        escrow_address, params, receiver_address, amount)

    program = base64.decodebytes(escrow_program.encode())
    lsig = transaction.LogicSigAccount(program)
    lsig_txn = transaction.LogicSigTransaction(txn, lsig)

    send_wait_transaction(client, lsig_txn)


def main():
    from mnemonics import (mnemonic2 as sender_mnemonic,
                           mnemonic1 as receiver_mnemonic)

    client = create_algod_client()
    receiver_address = mnemonic.to_public_key(receiver_mnemonic)

    teal = donation_escrow(receiver_address)
    escrow_program, escrow_address = compile_smart_signature(client, teal)

    print("Escrow program:", escrow_program)
    print("Escrow address:", escrow_address)

    print("Payment transaction: from sender to escrow")
    payment_transaction(client, sender_mnemonic, escrow_address, 2001000)

    print("Payment transaction: from escrow to receiver")
    lsig_payment_transaction(client, escrow_program,
                             escrow_address, receiver_address, 1000000)


if __name__ == '__main__':
    main()
