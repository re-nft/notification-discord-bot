from abc import ABC, abstractmethod
from typing import ClassVar
from notification_discord_bot import constants


class BlockchainContractMixin(ABC):
    @property
    @abstractmethod
    def query_url(self) -> str:
        pass


class EthereumAzraelMixin:
    query_url: ClassVar[str] = constants.ETHEREUM_AZRAEL_SUBGRAPH_URL


class EthereumSylvesterMixin:
    query_url: ClassVar[str] = constants.ETHEREUM_SYLVESTER_SUBGRAPH_URL


class MaticSylvesterMixin:
    query_url: ClassVar[str] = constants.MATIC_SYLVESTER_SUBGRAPH_URL


class AvalancheWhoopiMixin:
    query_url: ClassVar[str] = constants.AVALANCHE_WHOOPI_SUBGRAPH_URL
