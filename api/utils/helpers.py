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
