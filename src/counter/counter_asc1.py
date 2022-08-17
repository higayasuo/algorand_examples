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
    Subroutine,
    Expr,
    TealType,
    Add,
    Minus,
)
from algosdk.future.transaction import StateSchema


class GlobalVariables:
    count = Bytes("count")


class AppMethods:
    add = "add"
    subtract = "subtract"


global_schema = StateSchema(1, 0)
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
def create() -> Expr:
    return Seq(App.globalPut(GlobalVariables.count, Int(0)))


@Subroutine(TealType.none)
def no_op() -> Expr:
    return Seq(
        Cond(
            [Txn.application_args[0] == Bytes(AppMethods.add), add()],
            [Txn.application_args[0] == Bytes(AppMethods.subtract), subtract()],
        )
    )


@Subroutine(TealType.none)
def add() -> Expr:
    count = App.globalGet(GlobalVariables.count)
    return Seq(
        App.globalPut(GlobalVariables.count, Add(count, Int(1))),
    )


@Subroutine(TealType.none)
def subtract() -> Expr:
    count = App.globalGet(GlobalVariables.count)
    return Seq(
        If(
            count > Int(0),
            App.globalPut(GlobalVariables.count, Minus(count, Int(1))),
        ),
    )


def main() -> None:
    print(approval_program())


if __name__ == "__main__":
    main()
