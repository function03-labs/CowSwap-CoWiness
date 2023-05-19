from .web3 import get_receipt_from_txhash, create_contract
import web3.exceptions
from utils.instance_collect import fetch_order
from utils.create_contracts import settlement, erc20
from utils.helpers import *
import networkx as nx
# Create settlement and erc20 contracts
import matplotlib.pyplot as plt
from io import BytesIO


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
    # print("logs found are:", logs)
    processed_logs = []
    for log in logs:
        address = log["address"]
        processed_log = process_log(log)
        if processed_log is not None:
            processed_logs.append({"address": address, **processed_log})
    # print("processed logs are:", processed_logs)
    swaps = []
    expected_transfers = set()
    G = nx.DiGraph()
    G.add_node(settlement.address)

    for index, log in enumerate(processed_logs):
        args = log["args"]
        address = log["address"]
        # print("Log detected: ", log["event"], "\n log index is: ", index)
        if log["event"] == "Trade":
            oid = "0x" + str(
                hex(int.from_bytes(args["orderUid"],
                    byteorder="big", signed=False))
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
                

        if log["event"] == "Transfer":
            t = transferUid(address, args["from"], args["to"], args["value"])
            if t in expected_transfers:
                expected_transfers.remove(t)
            else:
                from_address = log["args"]["from"]
                to_address = log["args"]["to"]
                token_address = log["address"]
                value = log["args"]["value"]

                G.add_edge(from_address, to_address, value=value,
                           token=token_address)
            cycles = []

            plt.switch_backend('Agg')
            nx.draw(G, with_labels=True)
            plt.savefig("filename.png")

            cycles = nx.simple_cycles(G)

            for cycle in cycles:
                print(cycle, " cycle was")
                if settlement.address in cycle and len(cycle) > 1:
                    # cycle.append(settlement.address)
                    swap = {"sell_token": None, "sell_amount": 0,
                            "buy_token": None, "buy_amount": 0}
                    # get position of settlement address in cycle
                    i = cycle.index(settlement.address)

                    # get first address after settlement and address before
                    # settlement
                    address_to = cycle[(cycle.index(
                        settlement.address) + 1) % len(cycle)]
                    address_from = cycle[(cycle.index(
                    #     settlement.address) - 1) % len(cycle)]
                    # print(
                    #     "both addresses to and from",
                    #     address_to,
                    #     address_from,
                    #     "cycle",
                    #     cycle

                    # )
                    # get token and value of edge between settlement and address_to
                    token_to = G.edges[settlement.address, address_to]["token"]
                    value_to = G.edges[settlement.address, address_to]["value"]
                    # get token and value of edge between address_from and settlement
                    token_from = G.edges[address_from,
                                         settlement.address]["token"]
                    value_from = G.edges[address_from,
                                         settlement.address]["value"]

                    swap["sell_token"] = token_to
                    swap["sell_amount"] = value_to
                    swap["buy_token"] = token_from
                    swap["buy_amount"] = value_from
                    swaps.append({
                        "kind": "interaction",
                        # "target": args["target"],
                        **swap
                    })

                    # remove cycle from graph except settlement

                    # rearrange cycle list to start from settlement address at index i
                    cycle = cycle[i:] + cycle[:i]
                    # print("rearranged cycle is", cycle)
                    # remove all edges in cycle except settlement
                    for i in range(len(cycle)-1):
                        from_address = cycle[i]
                        to_address = cycle[i+1]
                        G.remove_edge(from_address, to_address)
                    # remove all nodes in cycle except settlement
                    for node in cycle:
                        if node != settlement.address:
                            G.remove_node(node)
                    # print("updated graph is", G.edges, " nodes: \n", G.nodes)


    return swaps, blockNumber
