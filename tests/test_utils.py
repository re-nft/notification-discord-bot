from notification_discord_bot.utils import normalize_ipfs_url


class TestNormalizeIPFSUrl:
    def test_normalize_ipfs_url(self):
        ipfs_url = "ipfs://QmctjdS9LFAK8KrMNXAKhQMrgtdPCGvhUWiEA4RbjqBWnV/Astrocat.mp4"
        expected_url = (
            "https://ipfs.io/ipfs/"
            "QmctjdS9LFAK8KrMNXAKhQMrgtdPCGvhUWiEA4RbjqBWnV/Astrocat.mp4"
        )
        assert normalize_ipfs_url(ipfs_url) == expected_url

    def test_not_normalize_ipfs_url(self):
        url = "https://ipfs.io/ipfs/QmctjdS9LFAK8KrMNXAKhQMrgtdPCGvhUWiEA4RbjqBWnV/Astrocat.mp4"
        expected_url = (
            "https://ipfs.io/ipfs/"
            "QmctjdS9LFAK8KrMNXAKhQMrgtdPCGvhUWiEA4RbjqBWnV/Astrocat.mp4"
        )
        assert normalize_ipfs_url(url) == expected_url
