from pyteal import (
    Approve,
    Reject,
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
)
from algosdk.future import transaction

from helper import (
    create_algod_client,
    compile_smart_contract,
    create_app,
    call_app,
    read_global_state,
)


class GlobalVariables:
    count = Bytes("count")


class AppMethods:
    add = "add"
    subtract = "subtract"


global_schema = transaction.StateSchema(1, 0)
local_schema = transaction.StateSchema(0, 0)


def handle_creation():
    return Seq(App.globalPut(GlobalVariables.count, Int(0)), Approve())


def add():
    count = App.globalGet(GlobalVariables.count)
    return Seq(
        App.globalPut(GlobalVariables.count, count + Int(1)),
        Approve(),
    )


def subtract():
    count = App.globalGet(GlobalVariables.count)
    return Seq(
        If(
            count > Int(0),
            App.globalPut(GlobalVariables.count, count - Int(1)),
        ),
        Approve(),
    )


def handle_noop():
    return Seq(
        Assert(Global.group_size() == Int(1)),
        Cond(
            [Txn.application_args[0] == Bytes(AppMethods.add), add()],
            [Txn.application_args[0] == Bytes(AppMethods.subtract), subtract()],
        ),
    )


def approval_program():
    return Cond(
        [Txn.application_id() == Int(0), handle_creation()],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop()],
        [Txn.on_completion() == OnComplete.OptIn, Reject()],
        [Txn.on_completion() == OnComplete.CloseOut, Reject()],
        [Txn.on_completion() == OnComplete.UpdateApplication, Reject()],
        [Txn.on_completion() == OnComplete.DeleteApplication, Reject()],
    )


def clear_state_program():
    return Approve()


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


if __name__ == "__main__":
    main()
