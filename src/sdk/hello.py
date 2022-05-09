from algosdk import account
from algosdk.v2client import algod

algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

def create_algod_client():
    return algod.AlgodClient(algod_token, algod_address)

def main():
    algod_client = create_algod_client()
    print(algod_client.versions())

main()
