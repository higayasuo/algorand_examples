from typing import cast
from algosdk import account, mnemonic


private_key, address = account.generate_account()
print("Address:", address)


mn = cast(str, mnemonic.from_private_key(private_key))
print("Mnemonic:", mn)
