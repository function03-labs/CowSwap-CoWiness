from .extract import get_swaps
from utils.order_prices import get_usd_prices_for_tx, get_usd_price_for_token
from ..utils.helpers import *


# This function computes the volume of tokens traded in and out of a transaction
def compute_volume(swaps):
    # Initialize dictionaries to store volume in and volume out for each token
    volume_in = {}
    volume_out = {}

    # Keep track of visited swaps to avoid double counting
    visited = set()

    # Iterate over all swaps in the transaction
    for id, swap in swaps.items():
        # If the swap is a trade, add the sell amount to the volume in dictionary
        if swap["kind"] == "trade":
            add_to_volume(volume_in, swap["sell_token"], swap["sell_amount"])
        # If the swap is an interaction, add the sell amount to the volume out dictionary
        elif swap["kind"] == "interaction":
            # Only add to volume out if this is the first time we're encountering this swap
            if id not in visited:
                add_to_volume(volume_out, swap["sell_token"], swap["sell_amount"])
                multi_hop = False

                # Check if there are any subsequent swaps that should be added to volume out
                for other_id, other_swap in swaps.items():
                    if should_add_to_visited(id, other_id, swap, other_swap, visited):
                        multi_hop = True
                        visited.add(other_id)
                        break

    # Convert all token names to lowercase for consistency
    volume_in = {k.lower(): v for k, v in volume_in.items()}
    volume_out = {k.lower(): v for k, v in volume_out.items()}

    # Return the volume in and volume out dictionaries
    return volume_in, volume_out


def compute_cowiness(tx_hash):
    swaps, blockNumber = get_swaps(tx_hash)
    swaps = {id: swap for id, swap in enumerate(swaps)}
    volume_in, volume_out = compute_volume(swaps)
    print(volume_in, volume_out)

    usd_prices = get_usd_prices_for_tx(tx_hash)

    volume_in_usd = calculate_usd_volume(blockNumber, volume_in, usd_prices)
    print(f"Total Volume In in USD: {volume_in_usd}")

    volume_out_usd = calculate_usd_volume(blockNumber, volume_out, usd_prices)
    print(f"Total Volume Out in USD: {volume_out_usd}")


# This function calculates the USD value of a given volume of tokens, using the token's price in USD
def calculate_usd_value(blockNumber, token, volume, usd_prices):
    # Check if the token's price is already in the usd_prices dictionary
    price = usd_prices.get(token)
    if price is None:
        # If not, get the token's price from the blockchain and add it to the dictionary
        price = get_usd_price_for_token(blockNumber, token)
        usd_prices[token] = price

    # Calculate the USD value of the volume using the token's price in USD
    amount = float(volume) / 10 ** int(price["decimals"])
    usd_value = amount * float(price["priceUsd"])

    # Return a dictionary with the amount, USD value, and token price information
    return {"amount": amount, "usd_value": usd_value, "token": price}


# This function calculates the USD volume of each token in a given volume dictionary, using the token's price in USD
def calculate_usd_volume(blockNumber, volume_dict, usd_prices):
    # Iterate over all tokens in the volume dictionary
    return {
        token: calculate_usd_value(blockNumber, token, vol, usd_prices)
        for token, vol in volume_dict.items()
    }


# This function computes the "Cow Index" of a given transaction, which is a measure of its profitability
def compute_cowiness_simple(tx_hash):
    # Get the swaps in the transaction and convert them to a dictionary with integer keys
    swaps, blockNumber = get_swaps(tx_hash)
    swaps = {id: swap for id, swap in enumerate(swaps)}

    # Compute the volume in and volume out dictionaries for the transaction
    volume_in, volume_out = compute_volume(swaps)

    # Get the USD prices for all tokens in the transaction
    usd_prices = get_usd_prices_for_tx(tx_hash)

    # Calculate the USD volume of each token in the volume in and volume out dictionaries
    volume_in_usd = calculate_usd_volume(blockNumber, volume_in, usd_prices)
    volume_out_usd = calculate_usd_volume(blockNumber, volume_out, usd_prices)

    # Calculate the total USD volume of tokens traded in and out of the transaction
    total_volume_out = sum([vol["usd_value"] for _, vol in volume_out_usd.items()])
    total_volume_in = sum([vol["usd_value"] for _, vol in volume_in_usd.items()])

    # Calculate the Cow Index using the total USD volume of tokens traded in and out of the transaction
    cow_value = (total_volume_in - total_volume_out) / total_volume_in

    # Return the Cow Index
    return cow_value


# This function computes detailed information about the "Cow Index" of a given transaction
def compute_cowiness_detailed(tx_hash):
    # Get the swaps in the transaction and convert them to a dictionary with integer keys
    swaps, blockNumber = get_swaps(tx_hash)
    swaps = {id: swap for id, swap in enumerate(swaps)}

    # Compute the volume in and volume out dictionaries for the transaction
    volume_in, volume_out = compute_volume(swaps)

    # Get the USD prices for all tokens in the transaction
    usd_prices = get_usd_prices_for_tx(tx_hash)

    # Calculate the USD volume of each token in the volume in and volume out dictionaries
    volume_in_usd = calculate_usd_volume(blockNumber, volume_in, usd_prices)
    volume_out_usd = calculate_usd_volume(blockNumber, volume_out, usd_prices)

    # Calculate the total USD volume of tokens traded in and out of the transaction
    total_volume_in_usd = sum([vol["usd_value"] for _, vol in volume_in_usd.items()])
    total_volume_out_usd = sum([vol["usd_value"] for _, vol in volume_out_usd.items()])

    # Calculate the Cow Index using the total USD volume of tokens traded in and out of the transaction
    cow_value = (total_volume_in_usd - total_volume_out_usd) / total_volume_in_usd

    # Create a dictionary with detailed information about the Cow Index and return it
    result = {
        "tx_hash": tx_hash,
        "total_volume_in_usd": total_volume_in_usd,
        "total_volume_out_usd": total_volume_out_usd,
        "cow_value": cow_value,
        "volume_in_usd": volume_in_usd,
        "volume_out_usd": volume_out_usd,
    }
    return result
