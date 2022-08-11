from algosdk.future.transaction import StateSchema
from pyteal import (
    Approve,
    Bytes,
    Cond,
    InnerTxnBuilder,
    Int,
    OnComplete,
    Seq,
    Subroutine,
    TealType,
    Txn,
    TxnField,
    TxnType,
    compileTeal,
    Mode,
    App,
    Btoi,
    Assert,
)


class AppMethods:
    init = "init"
    transfer_asset = "transfer_asset"


class GlobalVariables:
    asset_id = Bytes("asset_id")
    price = Bytes("price")


global_schema = StateSchema(2, 0)
local_schema = StateSchema(0, 0)


def approval_program() -> str:
    program = Seq(
        Cond(
            [Txn.application_id() == Int(0), create()],
            [Txn.on_completion() == OnComplete.NoOp, no_op()],
            [Txn.on_completion() == OnComplete.ClearState, Approve()],
            [Txn.on_completion() == OnComplete.CloseOut, Approve()],
            [Txn.on_completion() == OnComplete.DeleteApplication, Approve()],
            [Txn.on_completion() == OnComplete.OptIn, Approve()],
            [Txn.on_completion() == OnComplete.UpdateApplication, Approve()],
        ),
        Approve(),
    )
    return compileTeal(program, Mode.Application, version=6)


def clear_state_program() -> str:
    return compileTeal(Approve(), Mode.Application, version=6)


@Subroutine(TealType.none)
def create():
    return Seq()


@Subroutine(TealType.none)
def no_op():
    return Seq(
        Cond(
            [
                Txn.application_args[0] == Bytes(AppMethods.init),
                init(),
            ],
            [
                Txn.application_args[0] == Bytes(AppMethods.transfer_asset),
                transfer_asset(),
            ],
        ),
    )


@Subroutine(TealType.none)
def init():
    asset_id = Txn.assets[0]
    price = Btoi(Txn.application_args[1])
    return Seq(
        check_init(),
        App.globalPut(GlobalVariables.asset_id, asset_id),
        App.globalPut(GlobalVariables.price, price),
    )


@Subroutine(TealType.none)
def check_init():
    asset_id_ex = App.globalGetEx(Int(0), GlobalVariables.asset_id)
    return Seq(
        asset_id_ex,
        Assert(asset_id_ex.hasValue() == Int(0)),
        Assert(Txn.application_args.length() == Int(2)),
        Assert(Txn.assets.length() == Int(1)),
    )


@Subroutine(TealType.none)
def transfer_asset():
    return Seq(
        transfer_asset_txn(),
    )


@Subroutine(TealType.none)
def transfer_asset_txn():
    return Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_sender: Txn.accounts[1],
                TxnField.asset_receiver: Txn.sender(),
                TxnField.xfer_asset: Txn.assets[0],
                TxnField.asset_amount: Int(1),
            }
        ),
        InnerTxnBuilder.Submit(),
    )


def main():
    print(approval_program())


if __name__ == "__main__":
    main()
