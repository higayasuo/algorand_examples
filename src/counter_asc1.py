from pyteal import (
    Approve,
    Mode,
    compileTeal,
    Cond,
    If,
    Txn,
    OnComplete,
    Int,
    App,
    Bytes,
    Seq,
    Assert,
    Global,
    Expr,
)
from algosdk.future.transaction import StateSchema, ApplicationDeleteTxn
from algosdk.v2client.algod import AlgodClient
from algosdk.account import address_from_private_key

from helper import (
    create_algod_client,
    compile_smart_contract,
    create_app,
    call_app,
    read_global_state,
    sign_send_wait_transaction,
)


class GlobalVariables:
    count = Bytes("count")


class AppMethods:
    add = "add"
    subtract = "subtract"


global_schema = StateSchema(1, 0)
local_schema = StateSchema(0, 0)


def handle_creation() -> Expr:
    return Seq(App.globalPut(GlobalVariables.count, Int(0)), Approve())


def add() -> Expr:
    count = App.globalGet(GlobalVariables.count)
    return Seq(
        App.globalPut(GlobalVariables.count, count + Int(1)),
        Approve(),
    )


def subtract() -> Expr:
    count = App.globalGet(GlobalVariables.count)
    return Seq(
        If(
            count > Int(0),
            App.globalPut(GlobalVariables.count, count - Int(1)),
        ),
        Approve(),
    )


def handle_noop() -> Expr:
    return Seq(
        Assert(Global.group_size() == Int(1)),
        Cond(
            [Txn.application_args[0] == Bytes(AppMethods.add), add()],
            [Txn.application_args[0] == Bytes(AppMethods.subtract), subtract()],
        ),
    )


def approval_program() -> Expr:
    return Cond(
        [Txn.application_id() == Int(0), handle_creation()],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop()],
        [Txn.on_completion() == OnComplete.ClearState, Approve()],
        [Txn.on_completion() == OnComplete.CloseOut, Approve()],
        [Txn.on_completion() == OnComplete.DeleteApplication, Approve()],
        [Txn.on_completion() == OnComplete.OptIn, Approve()],
        [Txn.on_completion() == OnComplete.UpdateApplication, Approve()],
    )


def clear_state_program() -> Expr:
    return Approve()


def delete_app(client: AlgodClient, private_key: str, app_id: int) -> None:
    print("delete_app")
    sender = address_from_private_key(private_key)
    params = client.suggested_params()

    txn = ApplicationDeleteTxn(sender, params, index=app_id)
    sign_send_wait_transaction(client, txn, private_key)


def main():
    from accounts import test1_private_key as private_key

    client = create_algod_client()

    approval_teal = compileTeal(approval_program(), Mode.Application, version=6)
    approval = compile_smart_contract(client, approval_teal)

    clear_teal = compileTeal(clear_state_program(), Mode.Application, version=6)
    clear = compile_smart_contract(client, clear_teal)

    app_id = create_app(
        client, private_key, approval, clear, global_schema, local_schema
    )

    print(read_global_state(client, app_id))

    app_args = [AppMethods.add]
    call_app(client, private_key, app_id, app_args)
    print(read_global_state(client, app_id))

    app_args = [AppMethods.subtract]
    call_app(client, private_key, app_id, app_args)
    print(read_global_state(client, app_id))

    delete_app(client, private_key, app_id)


if __name__ == "__main__":
    main()
