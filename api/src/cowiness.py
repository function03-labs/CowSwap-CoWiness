from .swaps import get_swaps
from utils.order_prices import get_usd_prices_for_tx, get_usd_price_for_token
import argparse
import json


def is_within_tolerance(value1, value2, tolerance=0.01):
    return abs(value1 - value2) <= max(value1, value2) * tolerance


def compute_volume(swaps):
    volume_in = {}
    volume_out = {}

    visited = set()

    for id, swap in swaps.items():
        if swap["kind"] == "trade":
            if swap["sell_token"] not in volume_in:
                volume_in[swap["sell_token"]] = 0
            # if swap["buy_token"] not in volume_out:
            #     volume_out[swap["buy_token"]] = 0
            volume_in[swap["sell_token"]] += swap["sell_amount"]
            # volume_out[swap["buy_token"]] += swap["buy_amount"]

            # volume_out += swap["buy_amount"]
        elif swap["kind"] == "interaction":
            # volume_in += swap["sell_amount"]
            # volume_out += swap["buy_amount"]
            if swap["sell_token"] not in volume_out:
                volume_out[swap["sell_token"]] = 0
            # if swap["buy_token"] not in volume_out:
            #     volume_out[swap["buy_token"]] = 0
            if id not in visited:
                volume_out[swap["sell_token"]] += swap["sell_amount"]
                multi_hop = False
                for other_id, other_swap in swaps.items():
                    if (
                        other_id != id
                        and other_swap["kind"] == "interaction"
                        and other_swap["sell_token"] == swap["buy_token"]
                    ):
                        if is_within_tolerance(
                            swap["buy_amount"], other_swap["sell_amount"]
                        ):
                            multi_hop = True
                            visited.add(other_id)
                            # volume_out[other_swap["buy_token"]] += other_swap[
                            #     "buy_amount"
                            # ]
                            break
            # volume_out[swap["buy_token"]] += swap["buy_amount"]

            # make token address lower case in volume_in
    volume_in = {k.lower(): v for k, v in volume_in.items()}
    volume_out = {k.lower(): v for k, v in volume_out.items()}
    return volume_in, volume_out


def compute_cowiness(tx_hash):
    swaps, blockNumber = get_swaps(tx_hash)
    swaps = {id: swap for id, swap in enumerate(swaps)}
    # print(json.dumps(swaps, indent=2))
    volume_in, volume_out = compute_volume(swaps)
    print(volume_in, volume_out)
    # Calculate USD values for Volume In and Volume Out
    usd_prices = get_usd_prices_for_tx(tx_hash)

    # check token address for volume in is in usd_price or call get_usd_price_for_token on it and add it
    # Helper function to calculate USD value for a given token and volume
    def calculate_usd_value(token, volume):
        price = usd_prices.get(token)
        if price is None:
            price = get_usd_price_for_token(blockNumber, token)
            usd_prices[token] = price
        # print(usd_prices)
        amount = float(volume) / 10 ** int(price["decimals"])
        usd_value = amount * float(price["priceUsd"])
        return {"amount": amount, "usd_value": usd_value, "token": price}

    # Calculate USD values for Volume In
    volume_in_usd = {
        token: calculate_usd_value(token, vol) for token, vol in volume_in.items()
    }
    print(f"Total Volume In in USD: {volume_in_usd}")

    # Calculate USD values for Volume Out
    volume_out_usd = {
        token: calculate_usd_value(token, vol) for token, vol in volume_out.items()
    }
    print(f"Total Volume Out in USD: {volume_out_usd}")


def compute_cowiness_simple(tx_hash):
    swaps, blockNumber = get_swaps(tx_hash)
    swaps = {id: swap for id, swap in enumerate(swaps)}
    volume_in, volume_out = compute_volume(swaps)

    # Calculate USD values for Volume In
    usd_prices = get_usd_prices_for_tx(tx_hash)
    volume_in_usd = 0

    def calculate_usd_value(token, volume):
        price = usd_prices.get(token)
        if price is None:
            price = get_usd_price_for_token(blockNumber, token)
            usd_prices[token] = price
        # print(usd_prices)
        amount = float(volume) / 10 ** int(price["decimals"])
        usd_value = amount * float(price["priceUsd"])
        return {"amount": amount, "usd_value": usd_value, "token": price}

    # Calculate USD values for Volume In
    volume_in_usd = {
        token: calculate_usd_value(token, vol) for token, vol in volume_in.items()
    }

    # Calculate USD values for Volume Out
    volume_out_usd = {
        token: calculate_usd_value(token, vol) for token, vol in volume_out.items()
    }

    # Compute total volume out in USD
    total_volume_out = sum([vol["usd_value"] for _, vol in volume_out_usd.items()])

    total_volume_in = sum([vol["usd_value"] for _, vol in volume_in_usd.items()])

    # Compute CoW value as a float
    cow_value = (total_volume_in - total_volume_out) / total_volume_in

    return cow_value


def compute_cowiness_detailed(tx_hash):
    swaps, blockNumber = get_swaps(tx_hash)
    swaps = {id: swap for id, swap in enumerate(swaps)}
    volume_in, volume_out = compute_volume(swaps)

    # Calculate USD values for Volume In
    usd_prices = get_usd_prices_for_tx(tx_hash)
    volume_in_usd = {}
    for token, vol in volume_in.items():
        price = usd_prices.get(token)
        if price is None:
            price = get_usd_price_for_token(blockNumber, token)
            usd_prices[token] = price
        amount = float(vol) / 10 ** int(price["decimals"])
        usd_value = amount * float(price["priceUsd"])
        volume_in_usd[token] = {
            "amount": amount,
            "usd_value": usd_value,
            "token": price,
        }

    # Calculate USD values for Volume Out
    volume_out_usd = {}
    for token, vol in volume_out.items():
        price = usd_prices.get(token)
        if price is None:
            price = get_usd_price_for_token(blockNumber, token)
            usd_prices[token] = price
        amount = float(vol) / 10 ** int(price["decimals"])
        usd_value = amount * float(price["priceUsd"])
        volume_out_usd[token] = {
            "amount": amount,
            "usd_value": usd_value,
            "token": price,
        }

    # Compute total volume in and out in USD
    total_volume_in_usd = sum([vol["usd_value"] for _, vol in volume_in_usd.items()])
    total_volume_out_usd = sum([vol["usd_value"] for _, vol in volume_out_usd.items()])

    # Compute CoW value as a float
    cow_value = (total_volume_in_usd - total_volume_out_usd) / total_volume_in_usd

    # Create detailed result dictionary
    result = {
        "tx_hash": tx_hash,
        "total_volume_in_usd": total_volume_in_usd,
        "total_volume_out_usd": total_volume_out_usd,
        "cow_value": cow_value,
        "volume_in_usd": volume_in_usd,
        "volume_out_usd": volume_out_usd,
    }

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute cowiness of each order in a settlement."
    )

    parser.add_argument("txhash", type=str, help="Transaction hash of settlement.")

    args = parser.parse_args()

    txhash = args.txhash

    compute_cowiness(txhash)

# tx_hash="0xd531066dcf029e67ef9c1431106d7f03cdaf165de748ce121a355dbfadf775c3"   # No cow
# tx_hash = "0xfb9380a01bf8743fb9ea2a4b07dadd52dce701c4055dd1249473ffbd458ef561"  # 100% cow
# tx_hash = "0x6096b3f7d2c1ee87aebefbee0befd3ec5f79f9304c66bb5edf27603146faaccd"  # mixed
# tx_hash = "0x060c32d4ecbbd987d1d3c00761ee8ab7b189f7e3324658b9ab24fc0b6293d441"  # partial & complex
# tx_hash = "0xa797e6ca3952ff7bf4cbd4f465f1e49a2b2c1e8d12d1db3980fa87adbed4ff7c"  # partial
# compute_cowiness(tx_hash)
