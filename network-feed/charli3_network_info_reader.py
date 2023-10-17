"""Read C3 Network configuration"""

from pycardano import Address, UTxO, MultiAsset, BlockFrostChainContext
from datums import GenericData, AggDatum, OracleSettings, OraclePlatform


class Charli3NetworkInfoReader:
    """
    Charli3 Network Information Reader.

    Args:
        network_address (Address): The C3 network address to retrieve
    information for.
        minting_policy (MultiAsset): The minting policy used by the network.

    Attributes:
        network_address (Address): The network address being queried.
        network_minting_policy (MultiAsset): The minting policy of the network.
        aggregate_state_nft (MultiAsset): MultiAsset for the
    aggregate state NFT.
        network_feed_nft (MultiAsset): MultiAsset for the network feed NFT.
        context: BlockFrost context information.
    """

    def __init__(
        self,
        network_address: Address,
        minting_policy: MultiAsset,
        context: BlockFrostChainContext,
    ):
        self.network_address = network_address
        self.network_minting_policy = minting_policy
        self.aggregate_state_nft = MultiAsset.from_primitive(
            {minting_policy: {b"AggState": 1}}
        )
        self.network_feed_nft = MultiAsset.from_primitive(
            {minting_policy: {b"OracleFeed": 1}}
        )
        self.context = context

    def get_network_utxo(self) -> UTxO:
        """Retrieve the oracle's feed UTXO using the NFT identifier."""
        oracle_utxos = self.context.utxos(str(self.network_address))
        oracle_utxo_nft = next(
            utxo
            for utxo in oracle_utxos
            if utxo.output.amount.multi_asset == self.network_feed_nft
        )
        return oracle_utxo_nft

    def get_oracle_exchange_rate(self) -> int:
        """Get the oracle's feed exchange rate"""
        oracle_feed_utxo = self.get_network_utxo()
        oracle_inline_datum: GenericData = GenericData.from_cbor(
            oracle_feed_utxo.output.datum.cbor
        )
        return oracle_inline_datum.price_data.get_price()

    def get_network_timestamp(self) -> int:
        """Get the oracle's feed creation time"""
        oracle_feed_utxo = self.get_network_utxo()
        oracle_inline_datum: GenericData = GenericData.from_cbor(
            oracle_feed_utxo.output.datum.cbor
        )
        return oracle_inline_datum.price_data.get_timestamp()

    def get_network_expiration(self) -> int:
        """Get the oracle's feed expiration time"""
        oracle_feed_utxo = self.get_network_utxo()
        oracle_inline_datum: GenericData = GenericData.from_cbor(
            oracle_feed_utxo.output.datum.cbor
        )
        return oracle_inline_datum.price_data.get_expiry()

    def get_network_configuration(self):
        """Fetch the Aggregate UTxO Configuration Using the NFT Identifier"""
        aggregate_state_utxo = self.get_aggregate_state_utxo()
        aggregate_state_inline_datum: AggDatum = AggDatum.from_cbor(
            aggregate_state_utxo.output.datum.cbor
        )
        return aggregate_state_inline_datum.aggstate.ag_settings

    def get_price_rewards(self, rewards: OracleSettings):
        """
        Get price rewards from OracleSettings.

        Args:
            rewards (OracleSettings): An OracleSettings object containing
        price reward information.

        Returns:
            Tuple[float, float, float]: A tuple containing node_fee,
        aggregate_fee, and platform_fee.
        """
        return (
            rewards.os_node_fee_price.node_fee,
            rewards.os_node_fee_price.aggregate_fee,
            rewards.os_node_fee_price.platform_fee,
        )

    def get_platform_signatories_info(self, platform: OraclePlatform):
        """
        Get platform signatories information from OraclePlatform.

        Args:
            platform (OraclePlatform): An OraclePlatform object containing
        signatories info.

        Returns:
            Tuple[List[str], int]: A tuple containing a list of public key
        hashes and the threshold.
        """
        return (
            platform.os_platform.pmultisig_pkhs,
            platform.os_platform.pmultisig_threshold,
        )

    def get_aggregate_state_utxo(self) -> UTxO:
        """Retrieve the oracle's aggregate UTXO using the NFT identifier."""
        oracle_utxos = self.context.utxos(str(self.network_address))
        aggregate_state_utxo_nft = next(
            utxo
            for utxo in oracle_utxos
            if utxo.output.amount.multi_asset >= self.aggregate_state_nft
        )
        return aggregate_state_utxo_nft
