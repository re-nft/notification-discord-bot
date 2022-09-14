from notification_discord_bot.currency import pack_price, unpack_price


class TestUnpackPrice:
    def test_unpack_price_1_1():
        price = "1.1"
        packed_price = pack_price(price)
        unpacked_price = unpack_price(packedPrice)
        assert unpacked_price == price

    def test_unpack_price_1_0101():
        price = "1.0101"
        packed_price = pack_price(price)
        unpacked_price = unpack_price(packedPrice)
        assert unpacked_price == price

    def test_unpack_price_1_101():
        price = "1.101"
        packed_price = pack_price(price)
        unpacked_price = unpack_price(packedPrice)
        assert unpacked_price == price

    def test_unpack_price_1_0001():
        price = "1.0001"
        packed_price = pack_price(price)
        assert packed_price == "0x00010001"
        unpacked_price = unpack_price(packedPrice)
        assert unpacked_price == price

    def test_unpack_price_2874_3580():
        price = "2874.3580"
        packed_price = pack_price(price)
        unpacked_price = unpack_price(packedPrice)
        assert unpacked_price == price
