from pyteal import Approve, Mode, compileTeal


def approval_program():
    return Approve()


def clear_state_program():
    return Approve()


if __name__ == '__main__':
    teal = compileTeal(approval_program(), Mode.Application, version=6)
    print(teal)
