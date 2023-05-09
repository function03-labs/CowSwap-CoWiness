import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", ".env")))

w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_URL")))


def get_receipt_from_txhash(txhash):
    return w3.eth.getTransactionReceipt(txhash)


def create_contract(address, abi):
    return w3.eth.contract(address=address, abi=abi)
