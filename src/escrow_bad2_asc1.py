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
)


class AppMethods:
    transfer_asset = "transfer_asset"


global_schema = StateSchema(0, 0)
local_schema = StateSchema(0, 0)


def handle_creation():
    return Seq(
        Approve(),
    )


@Subroutine(TealType.none)
def transfer_asset_txn():
    return Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_sender: Txn.application_args[1],
                TxnField.asset_receiver: Txn.sender(),
                TxnField.xfer_asset: Txn.assets[0],
                TxnField.asset_amount: Int(1),
            }
        ),
        InnerTxnBuilder.Submit(),
    )


def transfer_asset():
    return Seq(
        transfer_asset_txn(),
        Approve(),
    )


def handle_noop():
    return Seq(
        Cond(
            [
                Txn.application_args[0] == Bytes(AppMethods.transfer_asset),
                transfer_asset(),
            ],
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
