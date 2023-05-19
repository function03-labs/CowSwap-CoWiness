from .web3 import get_receipt_from_txhash
import web3.exceptions
from utils.instance_collect import fetch_order
from utils.create_contracts import (
    settlement,
    erc20,
)
from utils.helpers import *

# Create settlement and erc20 contracts


def process_log(log):
    """
    Processes a log and returns the processed log if successful, otherwise returns None.
    """
    processed_log = None

    try:
        processed_log = try_process_settlement_trade(log)
    except web3.exceptions.MismatchedABI:
        pass

    if processed_log is None:
        try:
            processed_log = try_process_settlement_interaction(log)
        except web3.exceptions.MismatchedABI:
            pass

    if processed_log is None:
        try:
            processed_log = try_process_erc20_transfer(log)
        except web3.exceptions.MismatchedABI:
            pass

    return processed_log


def try_process_settlement_trade(log):
    """
    Attempts to process a settlement trade log and returns the processed log if successful, otherwise raises an exception.
    """
    return settlement.events.Trade().processLog(log)


def try_process_settlement_interaction(log):
    """
    Attempts to process a settlement interaction log and returns the processed log if successful, otherwise raises an exception.
    """
    return settlement.events.Interaction().processLog(log)


def try_process_erc20_transfer(log):
    """
    Attempts to process an erc20 transfer log and returns the processed log if successful, otherwise raises an exception.
    """
    return erc20.events.Transfer().processLog(log)


def collapse_interaction_transfers(accumulator, target, value, selector):
    """
    Collapses interaction transfers in the given accumulator into a swap and returns the swap as a list. Raises an exception if the accumulator cannot be collapsed.
    """
    tokens = {}

    for token_amount in accumulator["ins"]:
        token = token_amount["token"]
        amount = token_amount["amount"]
        if token not in tokens.keys():
            tokens[token] = 0
        tokens[token] += amount
    for token_amount in accumulator["outs"]:
        token = token_amount["token"]
        amount = token_amount["amount"]
        if token not in tokens.keys():
            tokens[token] = 0
        tokens[token] -= amount

    id = f"{target} @{selector}"
    entries = tokens.items()
    if len(entries) == 0:
        return []
    elif len(entries) != 2:
        raise RuntimeError(
            f"can't collapse interaction {id} transfers into a swap, entries are \n:",
            entries,
            "\n",
        )
    elif value != 0:
        raise RuntimeError(f"can't collapse interaction {id} with Ether value")

    tx0 = {"token": list(entries)[0][0], "amount": list(entries)[0][1]}
    tx1 = {"token": list(entries)[1][0], "amount": list(entries)[1][1]}

    if tx0["amount"] > 0:
        swap = {
            "sell_token": tx1["token"],
            "sell_amount": -tx1["amount"],
            "buy_token": tx0["token"],
            "buy_amount": tx0["amount"],
        }
    else:
        swap = {
            "sell_token": tx1["token"],
            "sell_amount": tx1["amount"],
            "buy_token": tx0["token"],
            "buy_amount": -tx0["amount"],
        }

    return [
        {
            "kind": "interaction",
            "target": target,
            "selector": hex(int.from_bytes(selector, byteorder="big", signed=False)),
            **swap,
        }
    ]


def get_swaps(tx_hash):
    """
    Returns a list of swaps and the block number for the given transaction hash.
    """
    receipt = get_receipt_from_txhash(tx_hash)
    blockNumber = receipt["blockNumber"]

    logs = receipt["logs"]
    # print("logs found are:", len(logs))
    processed_logs = []
    for log in logs:
        address = log["address"]
        processed_log = process_log(log)
        if processed_log is not None:
            processed_logs.append({"address": address, **processed_log})

    swaps = []
    accumulator = {}
    expected_transfers = set()

    for index, log in enumerate(processed_logs):
        args = log["args"]
        address = log["address"]
        # print("Log detected: ", log["event"], "\n log index is: ", index)
        if log["event"] == "Trade":
            oid = "0x" + str(
                hex(int.from_bytes(args["orderUid"], byteorder="big", signed=False))
            )[2:].zfill(112)
            order = fetch_order(oid)
            swaps.append(
                {
                    "kind": "trade",
                    "id": oid,
                    "sell_token": args["sellToken"],
                    "sell_amount": args["sellAmount"],
                    "buy_token": normalize_token(args["buyToken"]),
                    "buy_amount": args["buyAmount"],
                    "fee": args["feeAmount"],
                    "is_liquidity_order": order["isLiquidityOrder"],
                }
            )
            expected_transfers.add(
                transferUid(
                    args["sellToken"],
                    args["owner"],
                    settlement.address,
                    args["sellAmount"],
                )
            )

            if not is_eth(args.buyToken):
                expected_transfers.add(
                    transferUid(
                        args["buyToken"],
                        settlement.address,
                        normalize_receiver(order["receiver"], args["owner"]),
                        args["buyAmount"],
                    )
                )

        elif log["event"] == "Transfer":
            t = transferUid(address, args["from"], args["to"], args["value"])
            if t in expected_transfers:
                expected_transfers.remove(t)
            else:
                counterpart = (
                    args["to"] if args["to"] != settlement.address else args["from"]
                )
                if counterpart not in accumulator:
                    accumulator[counterpart] = {"ins": [], "outs": []}

                if args["to"] == settlement.address:
                    accumulator[counterpart]["ins"].append(
                        {"token": address, "amount": args["value"]}
                    )
                if args["from"] == settlement.address:
                    accumulator[counterpart]["outs"].append(
                        {"token": address, "amount": args["value"]}
                    )

        elif log["event"] == "Interaction":
            for counterpart, acc in accumulator.items():
                # print(accumulator, "acc")
                if len(acc["ins"]) >= 1 and len(acc["outs"]) >= 1:
                    swaps += collapse_interaction_transfers(
                        acc, args["target"], args["value"], args["selector"]
                    )
                    accumulator[counterpart] = {"ins": [], "outs": []}

    return swaps, blockNumber
