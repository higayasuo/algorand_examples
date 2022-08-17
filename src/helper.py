from base64 import b64decode
from typing import Any, Optional, cast

from algosdk.future.transaction import (
    Transaction,
    SignedTransaction,
    AssetConfigTxn,
    AssetOptInTxn,
    AssetTransferTxn,
    AssetDestroyTxn,
    wait_for_confirmation,
    OnComplete,
    ApplicationCreateTxn,
    ApplicationNoOpTxn,
    ApplicationDeleteTxn,
    PaymentTxn,
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
    return b64decode(cast(str, compile_response["result"]))


def send_wait_transaction(
    client: AlgodClient, signed_txns: list[SignedTransaction]
) -> Any:
    tx_id = cast(str, client.send_transactions(signed_txns))

    try:
        transaction_response = wait_for_confirmation(client, tx_id, 10)
        print("TXID: ", tx_id)
        print(
            "Result confirmed in round: {}".format(
                cast(int, transaction_response["confirmed-round"])
            )
        )
        return transaction_response

    except Exception as err:
        print(err)
        return


def sign_send_wait_transaction(
    client: AlgodClient, txn: Transaction, private_key: str
) -> Any:
    signed_txn = txn.sign(private_key)
    return send_wait_transaction(client, [signed_txn])


def sign_send_wait_group_transactions(
    client: AlgodClient, txns: list[Transaction], private_keys: list[str]
) -> Any:
    gid = calculate_group_id(txns)
    stxns: list[SignedTransaction] = []
    for i, txn in enumerate(txns):
        txn.group = gid
        stxns.append(txn.sign(private_keys[i]))
    return send_wait_transaction(client, stxns)


def create_asset(
    client: AlgodClient,
    private_key: str,
    asset_name: str,
    unit_name: str,
    total: int,
    decimals: int,
    default_frozen: bool = False,
    manager: Optional[str | bytes] = None,
    reserve: Optional[str | bytes] = None,
    freeze: Optional[str | bytes] = None,
    clawback: Optional[str | bytes] = None,
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

    asset_id = int(txn_res["asset-index"])
    print("create_asset()")
    print("Sender:", sender)
    print("Asset ID:", asset_id)

    return asset_id


def change_asset(
    client: AlgodClient,
    private_key: str,
    asset_id: int,
    manager: Optional[str | bytes],
    reserve: Optional[str | bytes],
    freeze: Optional[str | bytes],
    clawback: Optional[str | bytes],
) -> None:
    print("change_asset()")
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
    print("Asset ID:", asset_id)
    print("Manager:", manager)
    print("Reserve:", reserve)
    print("Freeze:", freeze)
    print("Clawback:", clawback)


def opt_in_asset(client: AlgodClient, private_key: str, asset_id: int) -> None:
    print("opt_in_asset()")
    sender = address_from_private_key(private_key)
    sp = client.suggested_params()

    txn = AssetOptInTxn(sender, sp, asset_id)
    sign_send_wait_transaction(client, txn, private_key)

    print("Sender:", sender)
    print("Asset ID:", asset_id)


def opt_out_asset(
    client: AlgodClient, private_key: str, asset_id: int, close_assets_to: str
) -> None:
    print("opt_out_asset()")
    sender = address_from_private_key(private_key)
    sp = client.suggested_params()

    txn = AssetTransferTxn(
        sender,
        sp,
        index=asset_id,
        receiver=close_assets_to,
        close_assets_to=close_assets_to,
        amt=0,
    )
    sign_send_wait_transaction(client, txn, private_key)

    print("Sender:", sender)
    print("Asset ID:", asset_id)


def transfer_asset(
    client: AlgodClient,
    private_key: str,
    receiver: str,
    asset_id: int,
    amt: int = 1,
) -> None:
    print("transfer_asset()")
    sender = address_from_private_key(private_key)
    sp = client.suggested_params()

    txn = AssetTransferTxn(
        sender=sender,
        sp=sp,
        receiver=receiver,
        index=asset_id,
        amt=amt,
    )
    sign_send_wait_transaction(client, txn, private_key)

    print("Sender:", sender)
    print("Receiver:", receiver)
    print("Asset ID:", asset_id)
    print("amount:", amt)


def revoke_asset(
    client: AlgodClient,
    private_key: str,
    revocation_target: str,
    receiver: str,
    asset_id: int,
    amt: int = 1,
) -> None:
    print("revoke_asset()")
    sender = address_from_private_key(private_key)
    sp = client.suggested_params()

    txn = AssetTransferTxn(
        sender=sender,
        sp=sp,
        revocation_target=revocation_target,
        receiver=receiver,
        index=asset_id,
        amt=amt,
    )
    sign_send_wait_transaction(client, txn, private_key)

    print("Sender:", sender)
    print("Revocation Target:", revocation_target)
    print("Receiver:", receiver)
    print("Asset ID:", asset_id)
    print("amount:", amt)


def destroy_asset(client: AlgodClient, private_key: str, asset_id: int) -> None:
    print("destroy_asset()")
    sender = address_from_private_key(private_key)
    sp = client.suggested_params()

    txn = AssetDestroyTxn(sender, sp, asset_id)
    sign_send_wait_transaction(client, txn, private_key)

    print("Sender:", sender)
    print("Asset ID:", asset_id)


def create_app(
    client: AlgodClient,
    private_key: str,
    approval_program: bytes,
    clear_program: bytes,
    global_schema: StateSchema,
    local_schema: StateSchema,
    foreign_assets: Optional[list[int]] = None,
    app_args: Optional[list[bytes]] = None,
) -> int:
    print("create_app()")
    sender = address_from_private_key(private_key)
    on_complete = OnComplete.NoOpOC.real
    sp = client.suggested_params()

    txn = ApplicationCreateTxn(
        sender,
        sp,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
        foreign_assets=foreign_assets,
        app_args=app_args,
    )

    txn_res = sign_send_wait_transaction(client, txn, private_key)
    app_id = int(txn_res["application-index"])

    print("Sender:", sender)
    print("Application ID:", app_id)

    return app_id


def call_app(
    client: AlgodClient,
    private_key: str,
    app_id: int,
    app_args: list[bytes],
    foreign_assets: Optional[list[int]] = None,
    accounts: Optional[list[int]] = None,
) -> None:
    print("call_app()")
    sender = address_from_private_key(private_key)
    sp = client.suggested_params()

    txn = ApplicationNoOpTxn(
        sender,
        sp,
        app_id,
        app_args,
        foreign_assets=foreign_assets,
        accounts=accounts,
    )

    sign_send_wait_transaction(client, txn, private_key)

    print("Sender:", sender)
    print("Application ID:", app_id)
    print("Application Args:", app_args)


def delete_app(client: AlgodClient, private_key: str, app_id: int) -> None:
    print("delete_app()")
    sender = address_from_private_key(private_key)
    sp = client.suggested_params()

    txn = ApplicationDeleteTxn(sender, sp, index=app_id)
    sign_send_wait_transaction(client, txn, private_key)

    print("Sender:", sender)
    print("Application ID:", app_id)


def fund(client: AlgodClient, private_key: str, receiver: str, amt: int) -> None:
    print("fund()")
    sender = address_from_private_key(private_key)
    sp = client.suggested_params()

    txn = PaymentTxn(sender, sp, receiver=receiver, amt=amt)
    sign_send_wait_transaction(client, txn, private_key)

    print("Sender:", sender)
    print("Receiver:", receiver)
    print("Amount:", amt)


def format_b64bytes(val: bytes) -> str | bytes:
    formatted_value = b64decode(val)

    try:
        return formatted_value.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return cast(str, encode_address(formatted_value))
        except Exception:
            pass

    return formatted_value


def format_state(state: list[dict[str, Any]]) -> dict[str, Any]:
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]
        formatted_key = b64decode(key).decode("utf-8")
        if int(value["type"]) == 1:
            # byte string
            formatted_value = format_b64bytes(value["bytes"])
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value["uint"]
    return formatted


def read_global_state(client: AlgodClient, app_id: int) -> dict[str, Any]:
    app_info = client.application_info(app_id)
    global_state = cast(
        list[dict[str, Any]],
        (
            app_info["params"]["global-state"]
            if "global-state" in app_info["params"]
            else []
        ),
    )
    return format_state(global_state)
