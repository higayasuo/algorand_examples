from pyteal import (Approve, Reject, Cond,
                    Txn, OnComplete, Int, App, Bytes, Seq, Assert, Global, Btoi,
                    TealType, If, Subroutine, TxnType, Gtxn, InnerTxnBuilder,
                    TxnField)
from algosdk.future.transaction import StateSchema


class GlobalVariables:
    owner = Bytes('owner')
    asset_id = Bytes('asset_id')
    amount = Bytes('amount')
    debug = Bytes('debug')


class AppMethods:
    init = 'init'
    buy = 'buy'


class Constants:
    royalty = Int(1000)


global_schema = StateSchema(2, 2)
local_schema = StateSchema(0, 0)


def handle_creation():
    return Seq(
        Assert(Global.group_size() == Int(1)),
        common_check_txn(Int(0)),
        Assert(Txn.application_args.length() == Int(0)),
        App.globalPut(GlobalVariables.owner, Global.creator_address()),
        Approve()
    )


@Subroutine(TealType.none)
def common_check_txn(txn_index):
    return Seq(
        Assert(txn_index < Global.group_size()),
        Assert(Gtxn[txn_index].rekey_to() == Global.zero_address()),
        Assert(Gtxn[txn_index].close_remainder_to() == Global.zero_address()),
        Assert(Gtxn[txn_index].asset_close_to() == Global.zero_address())
    )


def init():
    amount_ex = App.globalGetEx(
        Int(0), GlobalVariables.amount)
    amount = Btoi(Txn.application_args[1])

    return Seq(
        Assert(Global.group_size() == Int(1)),
        common_check_txn(Int(0)),
        amount_ex,
        Assert(amount_ex.hasValue() == Int(0)),
        Assert(Txn.application_args.length() == Int(2)),
        Assert(Txn.assets.length() == Int(1)),
        Assert(amount > Int(0)),
        App.globalPut(GlobalVariables.asset_id, Txn.assets[0]),
        App.globalPut(GlobalVariables.amount, amount),
        Approve()
    )


@Subroutine(TealType.none)
def check_application_call():
    return Seq(
        Assert(Gtxn[0].type_enum() == TxnType.ApplicationCall),
        Assert(Gtxn[0].application_args.length() == Int(1)),
        Assert(Gtxn[0].application_args[0] == Bytes(AppMethods.buy)),
    )


@Subroutine(TealType.none)
def check_payment(owner, amount):
    return Seq(
        Assert(Gtxn[1].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].receiver == owner),
        Assert(Gtxn[1].amount == amount),
    )


@Subroutine(TealType.none)
def check_buy_when_owner_is_creator(owner, buyer):
    return Seq(
        Assert(Global.group_size() == Int(1)),
        Assert(owner != buyer),
        check_application_call(),
    )


@Subroutine(TealType.none)
def transfor_asset(owner, buyer, asset_id):
    return Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_sender: owner,
            TxnField.asset_receiver: buyer,
            TxnField.xfer_asset: asset_id,
            TxnField.asset_amount: Int(1),
        }),
        InnerTxnBuilder.Submit(),
    )


@Subroutine(TealType.none)
def buy_when_owner_is_creator(owner, asset_id):
    buyer = Gtxn[0].sender()
    return Seq(
        check_buy_when_owner_is_creator(owner, buyer),
        transfor_asset(owner, buyer, asset_id),
    )


@Subroutine(TealType.none)
def buy_when_owner_is_not_creator():
    return Seq(
        App.globalPut(
            GlobalVariables.debug, Bytes('Buy from ownner'))
    )


def buy():
    creator = Global.creator_address()
    owner = App.globalGet(GlobalVariables.owner)
    asset_id = App.globalGet(GlobalVariables.asset_id)
    amount = App.globalGet(GlobalVariables.amount)

    return Seq(
        Assert(amount > Int(0)),
        If(creator == owner).Then(buy_when_owner_is_creator(owner, asset_id)).Else(
            buy_when_owner_is_not_creator()),
        Approve()
    )


def handle_noop():
    return Seq(
        # Assert(Global.group_size() == Int(1)),
        Cond(
            [Txn.application_args[0] == Bytes(
                AppMethods.init), init()],
            [Txn.application_args[0] == Bytes(
                AppMethods.buy), buy()],

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
