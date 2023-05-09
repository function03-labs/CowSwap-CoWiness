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
