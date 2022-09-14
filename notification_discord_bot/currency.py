import math
import re

from notification_discord_bot.constants import (
    BITSIZE_MAX_VALUE,
    HALF_BITSIZE,
    MAX_PRICE,
    NUM_BITS_IN_BYTE,
    PRICE_BITSIZE,
    ZEROS,
)


def decimal_to_padded_hex_string(number: int, bitsize: int) -> str:
    byte_count = math.ceil(bitsize / 8)
    max_bin_value = (2**bitsize) - 1
    if bitsize > 32:
        raise ValueError("Number above maximum value")
    if number < 0:
        number = max_bin_value + number + 1
    rhs = hex(number >> 0)[2:].upper().rjust(byte_count * 2, "0")
    return f"0x{rhs}"


def bytes_to_nibbles(byte_count: int) -> int:
    if byte_count < 1:
        raise ValueError("Invalid byteCount")
    return byte_count * 2


def to_padded_hex(number: int, bitsize: int) -> str:
    if bitsize > BITSIZE_MAX_VALUE:
        raise ValueError(f"bitsize ${bitsize} above maximum value ${BITSIZE_MAX_VALUE}")
    # conversion to unsigned form based on
    if number < 0:
        raise ValueError("unsigned number not supported")

    # 8 bits = 1 byteCount; 16 bits = 2 byteCount, ...
    byte_count = math.ceil(bitsize / NUM_BITS_IN_BYTE)

    # shifting 0 bits removes decimals
    # toString(16) converts into hex
    # .padStart(byteCount * 2, "0") adds byte
    # 1 nibble = 4 bits. 1 byte = 2 nibbles
    rhs = hex(number >> 0)[2:].upper().rjust(bytes_to_nibbles(byte_count), "0")
    return f"0x{rhs}"


def scale_decimal(num: str) -> float:
    MAX_LEN = 4
    for _ in range(0, MAX_LEN - len(num)):
        num = num + "0"
    return float(num)


def pack_price(price: str) -> str:
    if float(price) > MAX_PRICE:
        raise ValueError(f"Supplied price exceeds ${MAX_PRICE}")

    parts = str(price).split(".")
    whole = int(parts[0])
    if whole < 0:
        raise ValueError("Can't pack negative price")
    whole_hex = to_padded_hex(whole, HALF_BITSIZE)

    if len(parts) == 1:
        return whole_hex + "0000"
    if len(parts) != 2:
        raise RuntimeError("Price packing issue")

    decimal = scale_decimal(parts[1][0:4])

    return whole_hex + to_padded_hex(int(decimal), HALF_BITSIZE)[2:]


def unpack_price(price: str) -> float:
    num_hex = decimal_to_padded_hex_string(int(price, 16), PRICE_BITSIZE)[2:]
    whole = min(int(num_hex[0:4], 16), 9999)
    decimal = min(int(num_hex[4:], 16), 9999)

    decimal_str = str(decimal)
    MAX_LEN = 4
    for _ in range(0, MAX_LEN - len(decimal_str)):
        decimal_str = "0" + decimal_str

    return float(f"{whole}.{decimal_str}")


def get_multiplier(decimals: int) -> str:
    if 0 <= decimals <= 256 and not decimals % 1:
        return "1" + ZEROS[0:decimals]
    raise ValueError(f"Invalid decimal size: {decimals}")


def format_fixed(value: int, decimals: int = 0) -> str:
    multiplier = get_multiplier(decimals)

    negative = value < 0
    if negative:
        value = value * -1

    fraction = str(value % int(multiplier))
    while len(fraction) < len(multiplier) - 1:
        fraction = "0" + fraction

    # Strip trailing 0
    pattern = re.compile(r"^([0-9]*[1-9]|0)(0*)")
    m = pattern.match(fraction)
    if not m:
        raise ValueError("Cannot strip trailing zeros: {fraction}")
    fraction = m.groups()[0]

    whole = str(value // int(multiplier))

    if len(multiplier) == 1:
        new_value = whole
    else:
        new_value = whole + "." + fraction

    if negative:
        new_value = "-" + new_value

    return new_value


def parse_fixed(value: str, decimals: int = 0) -> int:
    multiplier = get_multiplier(decimals)

    # Is it negative?
    negative = value[0] == "-"
    if negative:
        value = value[1:]

    if value == ".":
        raise ValueError(f"Missing value: {value}")

    # Split it into a whole and fractional part
    comps = value.split(".")
    if len(comps) > 2:
        raise ValueError(f"Too many decimal points: {value}")

    whole = comps[0] if len(comps) >= 1 else "0"
    fraction = comps[1] if len(comps) == 2 else "0"

    # Trim trailing zeros
    while len(fraction) > 0 and fraction[-1] == "0":
        fraction = fraction[0 : len(fraction) - 1]

    # Check the fraction doesn't exceed our decimals size
    if len(fraction) > len(multiplier) - 1:
        raise ValueError("Fractional component exceeds decimals: underflow")

    # If decimals is 0, we have an empty string for fraction
    if fraction == "":
        fraction = "0"

    # Fully pad the string with zeros to get to wei
    while len(fraction) < len(multiplier) - 1:
        fraction += "0"

    whole_value = int(whole)
    fraction_value = int(fraction)

    wei = (whole_value * int(multiplier)) + fraction_value

    if negative:
        wei = wei * -1

    return wei
