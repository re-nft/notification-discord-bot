import pytest
from notification_discord_bot.currency import (
    bytes_to_nibbles,
    format_fixed,
    pack_price,
    parse_fixed,
    to_padded_hex,
    unpack_price,
)


class TestUnpackPrice:
    def test_unpack_price_1_1(self):
        price = "1.1"
        packed_price = pack_price(price)
        unpacked_price = unpack_price(packed_price)
        assert str(unpacked_price) == price

    def test_unpack_price_1_0101(self):
        price = "1.0101"
        packed_price = pack_price(price)
        unpacked_price = unpack_price(packed_price)
        assert str(unpacked_price) == price

    def test_unpack_price_1_101(self):
        price = "1.101"
        packed_price = pack_price(price)
        unpacked_price = unpack_price(packed_price)
        assert str(unpacked_price) == price

    def test_unpack_price_1_0001(self):
        price = "1.0001"
        packed_price = pack_price(price)
        assert packed_price == "0x00010001"
        unpacked_price = unpack_price(packed_price)
        assert str(unpacked_price) == price

    def test_unpack_price_2874_3580(self):
        price = "2874.3580"
        packed_price = pack_price(price)
        unpacked_price = unpack_price(packed_price)
        assert str(unpacked_price) == "2874.358"


class TestPackPrice:
    def test_packs_usual_domain(self):
        price = 21.42
        packed = pack_price(price)
        assert packed == "0x00151068"

    def test_packs_1_1(self):
        price = 1.1
        packed = pack_price(price)
        assert packed == "0x000103E8"

    def test_pads_usual_domain(self):
        price = 21
        padded = to_padded_hex(price, 32)
        assert padded == "0x00000015"

    def test_truncates_the_excess_decimals(self):
        price = 21.99999
        packed = pack_price(price)
        assert packed == "0x0015270F"

    def test_works_with_zero_decimal(self):
        price = 21.0
        packed = pack_price(price)
        assert packed == "0x00150000"

    def test_works_with_zero(self):
        price = 0
        packed = pack_price(price)
        assert packed == "0x00000000"

    def test_throws_on_unsigned(self):
        price = -1
        with pytest.raises(ValueError):
            pack_price(price)

    def test_throws_if_exceeds_9999_9999(self):
        price = 10000
        with pytest.raises(ValueError):
            pack_price(price)

    def test_throws_on_invalid_price(self):
        price = "11.22.33"
        with pytest.raises(ValueError):
            pack_price(price)

    def test_throws_if_bitsize_exceeds_32(self):
        bitsize = 33
        with pytest.raises(ValueError):
            to_padded_hex(1, bitsize)

    def test_throws_if_zero_bytecount(self):
        byte_count = 0
        with pytest.raises(ValueError):
            bytes_to_nibbles(byte_count)


class TestFormatFixed:
    def test_format_fixed_usdc_1(self):
        value = 1000000
        decimals = 6
        parsed = format_fixed(value, decimals)
        assert parsed == "1.0"

    def test_format_fixed_usdc_0_1(self):
        value = 100000
        decimals = 6
        parsed = format_fixed(value, decimals)
        assert parsed == "0.1"


class TestParseFixed:
    def test_parse_fixed_usdc_1(self):
        value = "1"
        decimals = 6
        parsed = parse_fixed(value, decimals)
        assert parsed == 1000000

    def test_parse_fixed_usdc_0_1(self):
        value = "0.1"
        decimals = 6
        parsed = parse_fixed(value, decimals)
        assert parsed == 100000
