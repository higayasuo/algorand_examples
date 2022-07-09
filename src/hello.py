from pyteal import Approve, Mode, compileTeal


def approval_program():
    program = Approve()
    return compileTeal(program, Mode.Application, version=6)


def clear_state_program():
    program = Approve()
    return compileTeal(program, Mode.Application, version=6)


if __name__ == '__main__':
    print(approval_program())
