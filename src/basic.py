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
)


def approval_program():
    return Approve()


def approval_program2():
    App.globalPut(Bytes("count"), Int(0))
    return Approve()


def approval_program3():
    return Seq(App.globalPut(Bytes("count"), Int(0)), Approve())


def approval_program4():
    num1 = Int(1)
    num2 = Int(2)
    return Seq(App.globalPut(Bytes("count"), num1 + num2), Approve())


def approval_program5():
    num1 = Int(1)
    num2 = Int(2)
    num3 = num1 + num2
    return Seq(App.globalPut(Bytes("count"), num3), Approve())


def approval_program6():
    num1 = Int(1)
    num2 = Int(2)
    num3 = num1 + num2
    num3 = Int(4)
    return Seq(App.globalPut(Bytes("count"), num3), Approve())


def approval_program7():
    num = ScratchVar(TealType.uint64)
    num.store(Int(0))
    return Seq(App.globalPut(Bytes("count"), num.load()), Approve())


def approval_program8():
    num = ScratchVar(TealType.uint64)

    return Seq(num.store(Int(1)), App.globalPut(Bytes("count"), num.load()), Approve())


def approval_program9():
    num1 = ScratchVar(TealType.uint64)
    num2 = ScratchVar(TealType.uint64)

    return Seq(
        num1.store(Int(1)),
        num2.store(Int(2)),
        App.globalPut(Bytes("count"), num1.load() + num2.load()),
        Approve(),
    )


@Subroutine(TealType.uint64)
def add(num1, num2):
    return num1 + num2


def approval_program10():
    return Seq(
        App.globalPut(Bytes("count"), add(Int(1), Int(2))),
        Approve(),
    )


def add2(num1, num2):
    return num1 + num2


def approval_program11():
    return Seq(
        App.globalPut(Bytes("count"), add2(Int(1), Int(2))),
        Approve(),
    )


@Subroutine(TealType.bytes)
def concat(bytes1, bytes2):
    return Concat(bytes1, bytes2)


def approval_program12():
    return Seq(
        App.globalPut(Bytes("count"), concat(Bytes("a"), Bytes("b"))),
        Approve(),
    )


@Subroutine(TealType.none)
def put_count():
    return Seq(
        App.globalPut(Bytes("count"), Int(0)),
    )


def approval_program13():
    return Seq(
        put_count(),
        Approve(),
    )


def approval_program14():
    aaa = Int(1)
    then_expr = App.globalPut(Bytes("debug"), Bytes("even"))
    else_expr = App.globalPut(Bytes("debug"), Bytes("odd"))
    return Seq(
        If(aaa % Int(2) == Int(0)).Then(then_expr).Else(else_expr),
        Approve(),
    )


def approval_program15():
    aaa = Int(1)
    one_expr = App.globalPut(Bytes("debug"), Bytes("one"))
    two_expr = App.globalPut(Bytes("debug"), Bytes("two"))
    return Seq(
        Cond(
            [aaa == Int(1), one_expr],
            [aaa == Int(2), two_expr],
        ),
        Approve(),
    )


def approval_program16():
    flag_ex = App.globalGetEx(Int(0), Bytes("flag"))
    return Seq(
        flag_ex,
        Assert(flag_ex.hasValue() == Int(0)),
        App.globalPut(Bytes("flag"), Int(1)),
        Approve(),
    )


if __name__ == "__main__":
    teal = compileTeal(approval_program(), Mode.Application, version=6)
    print(teal)
