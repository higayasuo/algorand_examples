from pyteal import (Approve, Reject, Mode, compileTeal, Cond, If,
                    Txn, OnComplete, Int, App, Bytes, Seq, Assert, Global,
                    ScratchVar, TealType)
from algosdk.future import transaction

from helper import create_algod_client, compile_smart_contract, create_app, call_app, read_global_state


class GlobalVariables:
    owner = Bytes("owner")
    asset_id = Bytes("asset_id")


class AppMethods:
    initialize = 'initialize'


global_schema = transaction.StateSchema(1, 1)
local_schema = transaction.StateSchema(0, 0)


def handle_creation():
    return Seq(
        Assert(Global.group_size() == Int(1)),
        App.globalPut(GlobalVariables.owner, Global.creator_address()),
        App.globalPut(GlobalVariables.asset_id, Txn.assets[0]),
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
