from ..api.src.web3 import get_receipt_from_txhash, create_contract


def create_settlement_contract():
    return create_contract(
        "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
        [
            {
                "anonymous": False,
                "inputs": [
                    # Settlement contract ABI inputs
                ],
                "name": "Trade",
                "type": "event",
            },
            {
                "anonymous": False,
                "inputs": [
                    # Settlement contract ABI inputs
                ],
                "name": "Interaction",
                "type": "event",
            },
        ],
    )


def create_erc20_contract():
    return create_contract(
        None,
        [
            {
                "anonymous": False,
                "inputs": [
                    # ERC20 contract ABI inputs
                ],
                "name": "Transfer",
                "type": "event",
            }
        ],
    )
