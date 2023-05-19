from src.web3 import get_receipt_from_txhash, create_contract


settlement = create_contract(
    "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
    [
        {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "owner",
                    "type": "address",
                },
                {
                    "indexed": False,
                    "internalType": "contract IERC20",
                    "name": "sellToken",
                    "type": "address",
                },
                {
                    "indexed": False,
                    "internalType": "contract IERC20",
                    "name": "buyToken",
                    "type": "address",
                },
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "sellAmount",
                    "type": "uint256",
                },
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "buyAmount",
                    "type": "uint256",
                },
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "feeAmount",
                    "type": "uint256",
                },
                {
                    "indexed": False,
                    "internalType": "bytes",
                    "name": "orderUid",
                    "type": "bytes",
                },
            ],
            "name": "Trade",
            "type": "event",
        },
        {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "target",
                    "type": "address",
                },
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "value",
                    "type": "uint256",
                },
                {
                    "indexed": False,
                    "internalType": "bytes4",
                    "name": "selector",
                    "type": "bytes4",
                },
            ],
            "name": "Interaction",
            "type": "event",
        },
    ],
)

erc20 = create_contract(
    None,
    [
        {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "from",
                    "type": "address",
                },
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "to",
                    "type": "address",
                },
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "value",
                    "type": "uint256",
                },
            ],
            "name": "Transfer",
            "type": "event",
        }
    ],
)
