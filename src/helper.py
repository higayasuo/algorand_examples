from base64 import b64decode

from algosdk.future.transaction import (
    Transaction,
    SignedTransaction,
    AssetConfigTxn,
    wait_for_confirmation,
    OnComplete,
    ApplicationCreateTxn,
    ApplicationNoOpTxn,
    StateSchema,
    calculate_group_id,
)
from algosdk.account import address_from_private_key
from algosdk.v2client.algod import AlgodClient
from algosdk.encoding import encode_address


algod_url = "https://node.testnet.algoexplorerapi.io:443"
algod_token = ""


def create_algod_client() -> AlgodClient:
    return AlgodClient(algod_token, algod_url)


def compile_smart_contract(client: AlgodClient, source_code: str) -> bytes:
    compile_response = client.compile(source_code)
    return b64decode(compile_response["result"])


def compile_smart_signature(client: AlgodClient, source_code: str) -> tuple[str, str]:
    compile_response = client.compile(source_code)
    return compile_response["result"], compile_response["hash"]


def send_wait_transaction(client: AlgodClient, signed_txns: list[SignedTransaction]):
    tx_id = client.send_transactions(signed_txns)

    try:
        transaction_response = wait_for_confirmation(client, tx_id, 10)
        print("TXID: ", tx_id)
        print(
            "Result confirmed in round: {}".format(
                transaction_response["confirmed-round"]
            )
        )
        return transaction_response

    except Exception as err:
        print(err)
        return


def sign_send_wait_transaction(client: AlgodClient, txn: Transaction, private_key: str):
    signed_txn = txn.sign(private_key)
    return send_wait_transaction(client, [signed_txn])


def sign_send_wait_group_transactions(
    client: AlgodClient, txns: list[Transaction], private_keys: list[str]
):
    gid = calculate_group_id(txns)
    stxns: list[SignedTransaction] = []
    for i, txn in enumerate(txns):
        txn.group = gid
        stxns.append(txn.sign(private_keys[i]))
    return send_wait_transaction(client, stxns)


def create_asset(
    client: AlgodClient,
    private_key: str,
    total: int = None,
    decimals: int = None,
    default_frozen: bool = None,
    unit_name: str = None,
    asset_name: str = None,
    manager: str = None,
    reserve: str = None,
    freeze: str = None,
    clawback: str = None,
) -> int:
    sender = address_from_private_key(private_key)
    sp = client.suggested_params()

    txn = AssetConfigTxn(
        sender=sender,
        sp=sp,
        total=total,
        decimals=decimals,
        default_frozen=default_frozen,
        unit_name=unit_name,
        asset_name=asset_name,
        manager=manager,
        reserve=reserve,
        freeze=freeze,
        clawback=clawback,
    )
    txn_res = sign_send_wait_transaction(client, txn, private_key)

    asset_id = txn_res["asset-index"]
    print("Sender:", sender)
    print("Created Asset ID:", asset_id)

    return asset_id


def change_asset(
    client: AlgodClient,
    private_key: str,
    asset_id: int,
    manager: str = None,
    reserve: str = None,
    freeze: str = None,
    clawback: str = None,
) -> None:
    sender = address_from_private_key(private_key)
    sp = client.suggested_params()

    txn = AssetConfigTxn(
        sender=sender,
        sp=sp,
        manager=manager,
        reserve=reserve,
        freeze=freeze,
        clawback=clawback,
    )
    sign_send_wait_transaction(client, txn, private_key)

    print("Sender:", sender)
    print("Updated Asset ID:", asset_id)
    print("Manager:", manager)
    print("Reserve:", reserve)
    print("Freeze:", freeze)
    print("Clawback:", clawback)


def create_app(
    client: AlgodClient,
    private_key: str,
    approval_program: bytes,
    clear_program: bytes,
    global_schema: StateSchema,
    local_schema: StateSchema,
    foreign_assets: list[int] = None,
    app_args: list[bytes] = None,
) -> int:
    sender = address_from_private_key(private_key)
    on_complete = OnComplete.NoOpOC.real
    params = client.suggested_params()

    txn = ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
        foreign_assets=foreign_assets,
        app_args=app_args,
    )

    txn_res = sign_send_wait_transaction(client, txn, private_key)
    app_id = txn_res["application-index"]

    print("Sender:", sender)
    print("Created Application ID:", app_id)

    return app_id


def call_app(
    client: AlgodClient,
    private_key: str,
    app_id: int,
    app_args: list[bytes] = None,
    foreign_assets: list[int] = None,
    accounts: list[int] = None,
):
    sender = address_from_private_key(private_key)
    params = client.suggested_params()

    txn = ApplicationNoOpTxn(
        sender,
        params,
        app_id,
        app_args,
        foreign_assets=foreign_assets,
        accounts=accounts,
    )

    sign_send_wait_transaction(client, txn, private_key)

    print("Sender:", sender)
    print("Application called:", app_id, app_args)


def format_b64bytes(val: bytes):
    formatted_value = b64decode(val)

    try:
        return formatted_value.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return encode_address(formatted_value)
        except Exception:
            pass

    return formatted_value


def format_state(state):
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]
        formatted_key = b64decode(key).decode("utf-8")
        if value["type"] == 1:
            # byte string
            formatted_value = format_b64bytes(value["bytes"])
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value["uint"]
    return formatted


def read_global_state(client: AlgodClient, app_id: int):
    app_info = client.application_info(app_id)
    global_state = (
        app_info["params"]["global-state"]
        if "global-state" in app_info["params"]
        else []
    )
    return format_state(global_state)


def main():
    from pyteal import compileTeal, Approve, Mode

    client = create_algod_client()
    teal = compileTeal(Approve(), Mode.Signature)

    prog, addr = compile_smart_signature(client, teal)
    print(prog, addr)


if __name__ == "__main__":
    main()
