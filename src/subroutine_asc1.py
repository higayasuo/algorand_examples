from pyteal import (Approve, Mode, compileTeal, Assert,
                    Int, Seq, Subroutine, TealType)


@Subroutine(TealType.none)
def sub():
    return Seq(
        Assert(Int(1) == Int(1))
    )


def approval_program():
    return Seq(sub(), sub(), Approve())


def clear_state_program():
    return Approve()


if __name__ == '__main__':
    teal = compileTeal(approval_program(), Mode.Application, version=6)
    print(teal)
