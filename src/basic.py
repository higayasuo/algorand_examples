from pyteal import (
    Approve,
    Mode,
    compileTeal,
    App,
    Bytes,
    Int,
    Seq,
    ScratchVar,
    TealType,
    If,
    Cond,
    Subroutine,
    Concat,
    Assert,
    Expr,
    Add,
)


def approval_program() -> str:
    return compileTeal(Approve(), Mode.Application, version=6)


def approval_program2() -> str:
    App.globalPut(Bytes("count"), Int(0))
    return compileTeal(Approve(), Mode.Application, version=6)


def approval_program3() -> str:
    return compileTeal(
        Seq(App.globalPut(Bytes("count"), Int(0)), Approve()),
        Mode.Application,
        version=6,
    )


def approval_program4() -> str:
    num1 = Int(1)
    num2 = Int(2)
    return compileTeal(
        Seq(App.globalPut(Bytes("count"), Add(num1, num2)), Approve()),
        Mode.Application,
        version=6,
    )


def approval_program5() -> str:
    num1 = Int(1)
    num2 = Int(2)
    num3 = num1 + num2
    return compileTeal(
        Seq(App.globalPut(Bytes("count"), num3), Approve()), Mode.Application, version=6
    )


def approval_program6() -> str:
    num1 = Int(1)
    num2 = Int(2)
    num3 = num1 + num2
    num3 = Int(4)
    return compileTeal(
        Seq(App.globalPut(Bytes("count"), num3), Approve()), Mode.Application, version=6
    )


def approval_program7() -> str:
    num = ScratchVar(TealType.uint64)
    num.store(Int(1))
    return compileTeal(
        Seq(App.globalPut(Bytes("count"), num.load()), Approve()),
        Mode.Application,
        version=6,
    )


def approval_program8() -> str:
    num = ScratchVar(TealType.uint64)

    return compileTeal(
        Seq(num.store(Int(1)), App.globalPut(Bytes("count"), num.load()), Approve()),
        Mode.Application,
        version=6,
    )


def approval_program9() -> str:
    num1 = ScratchVar(TealType.uint64)
    num2 = ScratchVar(TealType.uint64)

    return compileTeal(
        Seq(
            num1.store(Int(1)),
            num2.store(Int(2)),
            App.globalPut(Bytes("count"), Add(num1.load(), num2.load())),
            Approve(),
        ),
        Mode.Application,
        version=6,
    )


@Subroutine(TealType.uint64)
def add(num1: Expr, num2: Expr) -> Expr:
    return Add(num1, num2)


def approval_program10() -> str:
    return compileTeal(
        Seq(
            App.globalPut(Bytes("count"), add(Int(1), Int(2))),
            Approve(),
        ),
        Mode.Application,
        version=6,
    )


def add2(num1: Expr, num2: Expr) -> Expr:
    return Add(num1, num2)


def approval_program11() -> str:
    return compileTeal(
        Seq(
            App.globalPut(Bytes("count"), add2(Int(1), Int(2))),
            Approve(),
        ),
        Mode.Application,
        version=6,
    )


@Subroutine(TealType.bytes)
def concat(bytes1: Expr, bytes2: Expr) -> Expr:
    return Concat(bytes1, bytes2)


def approval_program12() -> str:
    return compileTeal(
        Seq(
            App.globalPut(Bytes("count"), concat(Bytes("a"), Bytes("b"))),
            Approve(),
        ),
        Mode.Application,
        version=6,
    )


@Subroutine(TealType.none)
def put_count() -> Expr:
    return Seq(
        App.globalPut(Bytes("count"), Int(0)),
    )


def approval_program13() -> str:
    return compileTeal(
        Seq(
            put_count(),
            Approve(),
        ),
        Mode.Application,
        version=6,
    )


def approval_program14() -> str:
    aaa = Int(1)
    then_expr = App.globalPut(Bytes("debug"), Bytes("even"))
    else_expr = App.globalPut(Bytes("debug"), Bytes("odd"))
    return compileTeal(
        Seq(
            If(aaa % Int(2) == Int(0)).Then(then_expr).Else(else_expr),
            Approve(),
        ),
        Mode.Application,
        version=6,
    )


def approval_program15() -> str:
    aaa = Int(1)
    one_expr = App.globalPut(Bytes("debug"), Bytes("one"))
    two_expr = App.globalPut(Bytes("debug"), Bytes("two"))
    return compileTeal(
        Seq(
            Cond(
                [aaa == Int(1), one_expr],
                [aaa == Int(2), two_expr],
            ),
            Approve(),
        ),
        Mode.Application,
        version=6,
    )


def approval_program16() -> str:
    flag_ex = App.globalGetEx(Int(0), Bytes("flag"))
    return compileTeal(
        Seq(
            flag_ex,
            Assert(flag_ex.hasValue() == Int(0)),
            App.globalPut(Bytes("flag"), Int(1)),
            Approve(),
        ),
        Mode.Application,
        version=6,
    )


def approval_program17() -> str:
    flag_ex = App.globalGetEx(Int(0), Bytes("flag"))
    return compileTeal(
        Seq(
            flag_ex,
            Assert(flag_ex.hasValue() == 0),
            App.globalPut(Bytes("flag"), Int(1)),
            Approve(),
        ),
        Mode.Application,
        version=6,
    )


if __name__ == "__main__":
    print(approval_program())
