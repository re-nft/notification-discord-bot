# TODO: file WIP
from notification_discord_bot.constants import HALF_BITSIZE, MAX_PRICE, PRICE_BITSIZE
from notification_discord_bot.renft import PaymentToken, ReNFTContract


def decimal_to_padded_hex_string(number: int, bitsize: int) -> str:
    pass


def to_padded_hex(number: int, bitsize: int) -> str:
    pass


def scale_decimal(num: str) -> str:
    pass


def pack_price(price: str) -> str:
    if float(price) > MAX_PRICE:
        raise ValueError(f"Supplied price exceeds ${MAX_PRICE}")

    parts = str(price).split(".")
    whole = int(parts[0])
    if whole < 0:
        raise ValueError("Can't pack negative price")
    whole_hex = to_padded_hex(int(whole), HALF_BITSIZE)

    if len(parts) == 1:
        return whole_hex + "0000"
    if len(parts) != 2:
        raise RuntimeError("Price packing issue")

    decimal = scale_decimal(parts[1][0:4])

    return whole_hex + to_padded_hex(int(decimal), HALF_BITSIZE)[2:]


def unpack_price(price: int) -> str:
    num_hex = decimal_to_padded_hex_string(price, PRICE_BITSIZE)[2:]
    whole = int(num_hex[0:4], 16)
    decimal = int(num_hex[4:], 16)
    if whole > 9999:
        whole = 9999
    if decimal > 9999:
        decimal = 9999

    decimal_str = str(decimal)
    MAX_LEN = 4
    for i in range(0, MAX_LEN - len(decimal_str)):
        decimal_str = "0" + decimal_str

    return f"${whole}.${decimal_str}"


def to_scaled_amount(value: str, contract: ReNFTContract, token: PaymentToken) -> str:
    # TODO: implement to_scaled_amount
    return value


def from_scaled_amount(value: str, contract: ReNFTContract, token: PaymentToken) -> str:
    # TODO: implement from_scaled_amount
    return value
