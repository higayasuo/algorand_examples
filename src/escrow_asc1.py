from pyteal import (Approve, Reject, Cond,
                    Txn, OnComplete, Int, App, Bytes, Seq, Assert, Global, Btoi)
from algosdk.future.transaction import StateSchema


class GlobalVariables:
    owner = Bytes("owner")
    asset_id = Bytes("asset_id")
    amount = Bytes("amount")


class AppMethods:
    initialize = 'initialize'


global_schema = StateSchema(2, 1)
local_schema = StateSchema(0, 0)


def handle_creation():
    return Seq(
        Assert(Global.group_size() == Int(1)),
        Assert(Txn.application_args.length() == Int(1)),
        App.globalPut(GlobalVariables.owner, Global.creator_address()),
        App.globalPut(GlobalVariables.asset_id, Txn.assets[0]),
        App.globalPut(GlobalVariables.amount, Btoi(Txn.application_args[0])),
        Approve()
    )


def initialize():
    return Seq(
        Approve()
    )


def handle_noop():
    return Seq(
        # Assert(Global.group_size() == Int(1)),
        Cond(
            [Txn.application_args[0] == Bytes(
                AppMethods.initialize), initialize()],

        )
    )


def approval_program():
    return Cond(
        [Txn.application_id() == Int(0), handle_creation()],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop()],
        [Txn.on_completion() == OnComplete.OptIn, Reject()],
        [Txn.on_completion() == OnComplete.CloseOut, Reject()],
        [Txn.on_completion() == OnComplete.UpdateApplication, Reject()],
        [Txn.on_completion() == OnComplete.DeleteApplication, Reject()]
    )


def clear_state_program():
    return Approve()


def main():
    pass


if __name__ == '__main__':
    main()
