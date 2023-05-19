import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

COWSWAP_SUBGRAPH_URL = os.environ.get("SUBGRAPH_ENDPOINT")


def get_usd_prices_for_order(order_id):
    query = """
    query GetOrder($id: ID!) {
      order(id: $id) {
        trades {
          buyAmount
          buyAmountUsd
          sellAmount
          sellAmountUsd
          sellToken {
            address
            decimals
            name
            id
          }
          buyToken {
            address
            decimals
            id
            name
          }
        }
      }
    }
    """

    variables = {"id": order_id}
    response = requests.post(
        COWSWAP_SUBGRAPH_URL, json={"query": query, "variables": variables}
    )
    data = response.json()["data"]["order"]["trades"]
    token_prices = {}

    for trade in data:
        if trade["sellAmountUsd"] == "0":
            trade["sellAmountUsd"] = trade["buyAmountUsd"]
        if trade["buyAmountUsd"] == "0":
            trade["buyAmountUsd"] = trade["sellAmountUsd"]
        sell_token_address = trade["sellToken"]["address"]
        sell_token_amount = float(trade["sellAmount"]) / 10 ** int(
            trade["sellToken"]["decimals"]
        )
        buy_token_amount = float(trade["buyAmount"]) / 10 ** int(
            trade["buyToken"]["decimals"]
        )

        sell_token_usd_price = float(trade["sellAmountUsd"]) / sell_token_amount
        buy_token_address = trade["buyToken"]["address"]
        buy_token_usd_price = float(trade["buyAmountUsd"]) / buy_token_amount

        if sell_token_address not in token_prices:
            token_prices[sell_token_address] = {
                "name": trade["sellToken"]["name"],
                "decimals": trade["sellToken"]["decimals"],
                "priceUsd": sell_token_usd_price,
                "amount": float(trade["sellAmount"])
                / 10 ** int(trade["sellToken"]["decimals"]),
            }
        else:
            token_prices[sell_token_address]["amount"] += trade["sellAmount"]

        if buy_token_address not in token_prices:
            token_prices[buy_token_address] = {
                "name": trade["buyToken"]["name"],
                "decimals": trade["buyToken"]["decimals"],
                "priceUsd": buy_token_usd_price,
                "amount": float(trade["buyAmount"])
                / 10 ** int(trade["buyToken"]["decimals"]),
            }
        else:
            token_prices[buy_token_address]["amount"] += trade["buyAmount"]

    return token_prices


def get_usd_prices_for_tx(tx_hash):
    query = """
    query GetTx($id: ID!) {
      settlement(id: $id){
        trades {
          order {
            id
          }
        }
      }
      }"""
    variables = {"id": tx_hash}
    response = requests.post(
        COWSWAP_SUBGRAPH_URL, json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["settlement"]["trades"]
    token_prices = {}
    for trade in data:
        order_id = trade["order"]["id"]
        order_prices = get_usd_prices_for_order(order_id)
        for token_address, order_elem in order_prices.items():
            if token_address not in token_prices:
                token_prices[token_address] = order_elem
            else:
                token_prices[token_address]["amount"] += order_elem["amount"]
    return token_prices


def get_usd_price_for_token(blockNumber, tokenAddress):
    query = """
    query GetTokenPrice($blockNumber: Int!, $tokenAddress: String!) {
      token(id: $tokenAddress, block: { number: $blockNumber }) {
        address
        id
        name
        priceUsd
        decimals
      }
    }
    """
    variables = {"blockNumber": blockNumber, "tokenAddress": tokenAddress}
    response = requests.post(
        COWSWAP_SUBGRAPH_URL, json={"query": query, "variables": variables}
    )
    data = response.json()["data"]["token"]
    return data
