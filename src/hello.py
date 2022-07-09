from pyteal import Approve, Mode, compileTeal


def approval():
    program = Approve()
    return compileTeal(program, Mode.Application)


def clear_state():
    program = Approve()
    return compileTeal(program, Mode.Application)


if __name__ == '__main__':
    print(approval())
