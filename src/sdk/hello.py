from sdk.util import create_algod_client


def main():
    algod_client = create_algod_client()
    print(algod_client.versions())


main()
