import os

from dotenv import load_dotenv
from algosdk import mnemonic, account

load_dotenv()

TEST1_MNEMONIC = os.getenv('TEST1_MNEMONIC')
TEST2_MNEMONIC = os.getenv('TEST2_MNEMONIC')
TEST3_MNEMONIC = os.getenv('TEST3_MNEMONIC')

test1_private_key = mnemonic.to_private_key(TEST1_MNEMONIC)
test2_private_key = mnemonic.to_private_key(TEST2_MNEMONIC)
test3_private_key = mnemonic.to_private_key(TEST3_MNEMONIC)


def main():
    print(account.address_from_private_key(test1_private_key))
    print(test1_private_key)
    print(account.address_from_private_key(test2_private_key))
    print(test2_private_key)
    print(account.address_from_private_key(test3_private_key))
    print(test3_private_key)


if __name__ == '__main__':
    main()
