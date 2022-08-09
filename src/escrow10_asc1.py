from algosdk.future.transaction import StateSchema
from pyteal import (
    Approve,
    Bytes,
    Cond,
    Gtxn,
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
        Approve(),
    )


@Subroutine(TealType.none)
def opt_in():
    return Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_sender: Gtxn[0].sender(),
                TxnField.asset_receiver: Gtxn[0].sender(),
                TxnField.xfer_asset: Gtxn[0].assets[0],
                TxnField.asset_amount: Int(0),
            }
        ),
        InnerTxnBuilder.Submit(),
    )


@Subroutine(TealType.none)
def transfer_asset():
    return Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_sender: Gtxn[0].accounts[1],
                TxnField.asset_receiver: Gtxn[0].sender(),
                TxnField.xfer_asset: Gtxn[0].assets[0],
                TxnField.asset_amount: Int(1),
            }
        ),
        InnerTxnBuilder.Submit(),
    )


def buy():
    return Seq(
        opt_in(),
        transfer_asset(),
        Approve(),
    )


def handle_noop():
    return Seq(
        Cond(
            [Txn.application_args[0] == Bytes(AppMethods.buy), buy()],
        )
    )


def approval_program():
    return Cond(
        [Txn.application_id() == Int(0), handle_creation()],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop()],
        [Txn.on_completion() == OnComplete.ClearState, Approve()],
        [Txn.on_completion() == OnComplete.CloseOut, Approve()],
        [Txn.on_completion() == OnComplete.DeleteApplication, Approve()],
        [Txn.on_completion() == OnComplete.OptIn, Approve()],
        [Txn.on_completion() == OnComplete.UpdateApplication, Approve()],
    )


def clear_state_program():
    return Approve()


def main():
    pass


if __name__ == "__main__":
    main()
