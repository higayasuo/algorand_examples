mnemonic1 = "birth april scatter wide stool resist song hobby unaware rabbit marine convince "\
    "goat planet exhaust size visual cupboard squirrel isolate obvious will tennis about maple"
mnemonic2 = "similar solution pepper old sand trend twin joke dolphin tank salad "\
    "shoe across latin robust broccoli hold exact kite sorry follow man excite absent magic"
mnemonic3 = "fever youth tiny fog friend burden police guess text arrange bridge pen warrior "\
    "volcano forward position club fabric shrug moment rotate rotate armor absent hedgehog"


def main():
    from algosdk import mnemonic

    print(mnemonic.to_public_key(mnemonic1))
    print(mnemonic.to_public_key(mnemonic2))
    print(mnemonic.to_public_key(mnemonic3))


if __name__ == '__main__':
    main()
