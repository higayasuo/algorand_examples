from pyteal import (Approve, Reject, Mode, compileTeal, Cond, If,
                    Txn, OnComplete, Int, App, Bytes, Seq, Assert, Global,
                    ScratchVar, TealType)
from algosdk.future import transaction
from algosdk import mnemonic

from helper import create_algod_client, compile_smart_contract, create_app, call_app, read_global_state


handle_creation = Seq(
    App.globalPut(Bytes("Count"), Int(0)),
    Approve()
)

scratchCount = ScratchVar(TealType.uint64)

add = Seq(
    scratchCount.store(App.globalGet(Bytes("Count"))),
    App.globalPut(Bytes("Count"), scratchCount.load() + Int(1)),
    Approve()
)

subtract = Seq(
    scratchCount.store(App.globalGet(Bytes("Count"))),
    If(scratchCount.load() > Int(0),
       App.globalPut(Bytes("Count"), scratchCount.load() - Int(1)),
       ),
    Approve()
)

handle_noop = Seq(
    # First, lets fail immediately if this transaction is grouped with any others
    Assert(Global.group_size() == Int(1)),
    Cond(
        [Txn.application_args[0] == Bytes("Add"), add],
        [Txn.application_args[0] == Bytes("Subtract"), subtract]
    )
)

handle_optin = Reject()
handle_closeout = Reject()
handle_updateapp = Reject()
handle_deleteapp = Reject()


def approval_program():
    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )
    return compileTeal(program, Mode.Application, version=6)


def clear_state_program():
    program = Approve()
    return compileTeal(program, Mode.Application, version=6)


def main():
    from mnemonics import mnemonic2

    client = create_algod_client()

    approval = compile_smart_contract(client, approval_program())
    clear = compile_smart_contract(client, clear_state_program())
    private_key = mnemonic.to_private_key(mnemonic2)
    global_schema = transaction.StateSchema(1, 0)
    local_schema = transaction.StateSchema(0, 0)

    app_id = create_app(client, private_key, approval,
                        clear, global_schema, local_schema)

    print(read_global_state(client, app_id))

    app_args = ["Add"]
    print("Call Add")
    call_app(client, private_key, app_id, app_args)
    print(read_global_state(client, app_id))

    app_args = ["Subtract"]
    print("Call Subtract")
    call_app(client, private_key, app_id, app_args)
    print(read_global_state(client, app_id))


if __name__ == '__main__':
    main()
