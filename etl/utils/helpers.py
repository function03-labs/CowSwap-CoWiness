from eth_abi import encode_abi, decode_abi
from web3.constants import ADDRESS_ZERO


def normalize_receiver(receiver, owner):
    """
    Normalizes the receiver address by returning the owner address if the receiver is ADDRESS_ZERO, otherwise returns the receiver address.
    """
    return receiver if receiver != ADDRESS_ZERO else owner


def is_eth(token):
    """
    Returns True if the token address is for Ether, False otherwise.
    """
    return token.lower() == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"


def normalize_token(token):
    """
    Normalizes the token address by returning the address of WETH if the token is Ether, otherwise returns the token address.
    """
    return "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" if is_eth(token) else token


def transferUid(address, from_, to, value):
    """
    Encodes a transfer UID with the given parameters and returns the encoded data.
    """
    return encode_abi(
        ["address", "address", "address", "uint256"],
        [address, from_, to, value],
    )


def is_within_tolerance(value1, value2, tolerance=0.01):
    """
    Check if the difference between two values is within a specified tolerance.

    :param value1: First value to compare
    :param value2: Second value to compare
    :param tolerance: Tolerance value to check against (default: 0.01)
    :return: True if the difference is within tolerance, False otherwise
    """
    return abs(value1 - value2) <= max(value1, value2) * tolerance


def add_to_volume(volume_dict, token, amount):
    """
    Add the specified amount to the volume dictionary for the given token.

    :param volume_dict: Dictionary containing token volumes
    :param token: Token to add the volume for
    :param amount: Amount to be added
    """
    if token not in volume_dict:
        volume_dict[token] = 0
    volume_dict[token] += amount


def should_add_to_visited(id, other_id, swap, other_swap, visited):
    """
    Check if an interaction should be added to the visited set.

    :param id: Current swap ID
    :param other_id: Other swap ID to compare
    :param swap: Current swap
    :param other_swap: Other swap to compare
    :param visited: Set containing visited swaps
    :return: True if the interaction should be added to the visited set, False otherwise
    """
    return (
        other_id != id
        and other_swap["kind"] == "interaction"
        and other_swap["sell_token"] == swap["buy_token"]
        and is_within_tolerance(swap["buy_amount"], other_swap["sell_amount"])
        and other_id not in visited
    )
