from algosdk import account, mnemonic


private_key, address = account.generate_account()
print('Address:', address)


mn = mnemonic.from_private_key(private_key)
print('Mnemonic:', mn)
