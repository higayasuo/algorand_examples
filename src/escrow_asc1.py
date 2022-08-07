from algosdk.future.transaction import StateSchema
from pyteal import (
    App,
    Approve,
    Assert,
    Btoi,
    Bytes,
    Cond,
    Global,
    Gtxn,
    If,
    InnerTxnBuilder,
    Int,
    OnComplete,
    Reject,
    Seq,
    Subroutine,
    TealType,
    Txn,
    TxnField,
    TxnType,
)


class GlobalVariables:
    owner = Bytes("owner")
    asset_id = Bytes("asset_id")
    amount = Bytes("amount")
    debug = Bytes("debug")


class AppMethods:
    init = "init"
    buy = "buy"


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
        Approve(),
    )


@Subroutine(TealType.none)
def common_check_txn(txn_index):
    return Seq(
        Assert(txn_index < Global.group_size()),
        Assert(Gtxn[txn_index].rekey_to() == Global.zero_address()),
        Assert(Gtxn[txn_index].close_remainder_to() == Global.zero_address()),
        Assert(Gtxn[txn_index].asset_close_to() == Global.zero_address()),
    )


def init():
    amount_ex = App.globalGetEx(Int(0), GlobalVariables.amount)
    amount = Btoi(Txn.application_args[1])

    return Seq(
        Assert(Global.group_size() == Int(2)),
        common_check_txn(Int(0)),
        common_check_txn(Int(1)),
        amount_ex,
        Assert(amount_ex.hasValue() == Int(0)),
        Assert(Gtxn[0].sender() == Global.creator_address()),
        Assert(Gtxn[0].application_args.length() == Int(2)),
        Assert(Gtxn[0].assets.length() == Int(1)),
        Assert(amount > Int(0)),
        Assert(Gtxn[1].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].sender() == Global.creator_address()),
        Assert(Gtxn[1].receiver() == Global.current_application_address()),
        App.globalPut(GlobalVariables.asset_id, Txn.assets[0]),
        App.globalPut(GlobalVariables.amount, amount),
        Approve(),
    )


@Subroutine(TealType.none)
def check_opt_in(tx_index, buyer):
    return Seq(
        Assert(Gtxn[tx_index].type_enum() == TxnType.AssetTransfer),
        # App.globalPut(GlobalVariables.debug, Gtxn[tx_index].asset_sender()),
        # Assert(Gtxn[tx_index].asset_sender() == buyer),
        # Assert(Gtxn[tx_index].asset_receiver() == buyer),
        Assert(Gtxn[tx_index].asset_amount() == Int(0)),
    )


@Subroutine(TealType.none)
def check_buy_call(tx_index):
    return Seq(
        Assert(Gtxn[tx_index].type_enum() == TxnType.ApplicationCall),
        Assert(Gtxn[tx_index].application_args.length() == Int(1)),
        Assert(Gtxn[tx_index].application_args[0] == Bytes(AppMethods.buy)),
    )


@Subroutine(TealType.none)
def check_buy_payment(owner, amount):
    return Seq(
        Assert(Gtxn[1].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].receiver == owner),
        Assert(Gtxn[1].amount == amount),
    )


@Subroutine(TealType.none)
def transfor_asset(owner, buyer, asset_id):
    return Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_sender: owner,
                TxnField.asset_receiver: buyer,
                TxnField.xfer_asset: asset_id,
                TxnField.asset_amount: Int(1),
            }
        ),
        InnerTxnBuilder.Submit(),
    )


@Subroutine(TealType.none)
def buy_when_owner_is_creator(owner, asset_id):
    buyer = Gtxn[0].sender()
    return Seq(
        Assert(Global.group_size() == Int(2)),
        common_check_txn(Int(0)),
        common_check_txn(Int(1)),
        Assert(owner != buyer),
        check_opt_in(Int(0), buyer),
        check_buy_call(Int(1)),
        # transfor_asset(owner, buyer, asset_id),
    )


@Subroutine(TealType.none)
def buy_when_owner_is_not_creator():
    return Seq(App.globalPut(GlobalVariables.debug, Bytes("Buy from ownner")))


def buy():
    creator = Global.creator_address()
    owner = App.globalGet(GlobalVariables.owner)
    asset_id = App.globalGet(GlobalVariables.asset_id)
    amount = App.globalGet(GlobalVariables.amount)

    return Seq(
        Assert(amount > Int(0)),
        If(creator == owner)
        .Then(buy_when_owner_is_creator(owner, asset_id))
        .Else(buy_when_owner_is_not_creator()),
        Approve(),
    )


def handle_noop():
    return Seq(
        # Assert(Global.group_size() == Int(1)),
        Cond(
            [Txn.application_args[0] == Bytes(AppMethods.init), init()],
            [Txn.application_args[0] == Bytes(AppMethods.buy), buy()],
        )
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
    pass


if __name__ == "__main__":
    main()
