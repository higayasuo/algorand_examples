import base64

from algosdk.future import transaction
from algosdk import account
from algosdk.v2client import algod

algod_url = "https://node.testnet.algoexplorerapi.io:443"
algod_token = ""


def create_algod_client():
    return algod.AlgodClient(algod_token, algod_url)


def compile_smart_contract(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response['result'])


def compile_smart_signature(client, source_code):
    compile_response = client.compile(source_code)
    return compile_response['result'], compile_response['hash']


def send_wait_transaction(client, signed_txn):
    tx_id = client.send_transactions([signed_txn])

    try:
        transaction_response = transaction.wait_for_confirmation(
            client, tx_id, 5)
        print("TXID: ", tx_id)
        print("Result confirmed in round: {}".format(
            transaction_response['confirmed-round']))
        return transaction_response

    except Exception as err:
        print(err)
        return


def sign_send_wait_transaction(client, txn, private_key):
    signed_txn = txn.sign(private_key)

    return send_wait_transaction(client, signed_txn)


def create_app(client, private_key, approval_program, clear_program, global_schema, local_schema):
    sender = account.address_from_private_key(private_key)
    on_complete = transaction.OnComplete.NoOpOC.real
    params = client.suggested_params()

    txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                           approval_program, clear_program,
                                           global_schema, local_schema)

    txn_res = sign_send_wait_transaction(client, txn, private_key)
    app_id = txn_res['application-index']

    print("Created new app-id:", app_id)

    return app_id


def format_state(state):
    formatted = {}
    for item in state:
        key = item['key']
        value = item['value']
        formatted_key = base64.b64decode(key).decode('utf-8')
        if value['type'] == 1:
            # byte string
            formatted_value = base64.b64decode(
                value['bytes']).decode('utf-8')
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value['uint']
    return formatted


def read_global_state(client, app_id):
    app_info = client.application_info(app_id)
    global_state = app_info["params"]["global-state"] if "global-state" in app_info['params'] else []
    return format_state(global_state)


def call_app(client, private_key, app_id, app_args):
    sender = account.address_from_private_key(private_key)
    params = client.suggested_params()

    txn = transaction.ApplicationNoOpTxn(sender, params, app_id, app_args)

    sign_send_wait_transaction(client, txn, private_key)

    print("Application called")


def main():
    from pyteal import compileTeal, Approve, Mode

    client = create_algod_client()
    teal = compileTeal(Approve(), Mode.Signature)

    prog, addr = compile_smart_signature(client, teal)
    print(prog, addr)
    print(base64.decodebytes(prog.encode()))


if __name__ == '__main__':
    main()
