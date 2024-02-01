"""Read C3 Network configuration"""

from pycardano import Address,  MultiAsset, BlockFrostChainContext
from .datums import GenericData, AggDatum, OracleSettings, OraclePlatform
from datetime import datetime


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
        minting_policy: str,
        context,
    ):
        self.network_address = network_address
        self.aggregate_state_nft = MultiAsset.from_primitive(
            {minting_policy: {b"AggState": 1}}
        )
        self.network_feed_nft = MultiAsset.from_primitive(
            {minting_policy: {b"OracleFeed": 1}}
        )
        self.context = context

    def format_timestamp(self, timestamp):
        """Convert epoch to humnan"""
        return datetime.utcfromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")


    def display_oracle_feed(self):
        """Get the oracle's feed exchange rate"""
        try:
            oracle_utxos = self.context.utxos(str(self.network_address))
            print(oracle_utxos)

            oracle_feed_utxo = None
            for utxo in oracle_utxos:
                if utxo.output.amount.multi_asset == self.network_feed_nft:
                    oracle_feed_utxo = utxo
                    break
            else:
                raise ValueError("No Oracle Feed UTXO found matching the network feed NFT.")

            print(oracle_feed_utxo)
            oracle_inline_datum: GenericData = GenericData.from_cbor(
                oracle_feed_utxo.output.datum.cbor
            )

            print(oracle_inline_datum)
            price = int(oracle_inline_datum.price_data.get_price() / 1000000)
            creation_time = self.format_timestamp(
                oracle_inline_datum.price_data.get_timestamp()
            )
            expiration_time = self.format_timestamp(
                oracle_inline_datum.price_data.get_expiry()
            )

            feed_info = f"""Last Price: {price}
    Creation time: {creation_time}
    Expiration time: {expiration_time}"""

            print(feed_info)

        except ValueError as e:
            print(f"Error retrieving oracle feed: {e}")
        # except Exception as e:
        #     print(f"An unexpected error occurred: {e}")

    def get_network_configuration(self):
        """Fetch the Aggregate UTxO Configuration Using the NFT Identifier"""
        try:
            oracle_utxos = self.context.utxos(str(self.network_address))
            print(oracle_utxos)

            for utxo in oracle_utxos:
                if utxo.output.amount.multi_asset >= self.aggregate_state_nft:
                    aggregate_state_utxo = utxo
                    break
            else:
                raise ValueError("No matching Aggregate State UTXO found.")

            aggregate_state_inline_datum: AggDatum = AggDatum.from_cbor(
                aggregate_state_utxo.output.datum.cbor
            )

            return aggregate_state_inline_datum.aggstate.ag_settings

        except ValueError as e:
            # Log the error or re-raise with more context if necessary
            raise ValueError("Failed to fetch network configuration: " + str(e))
        except Exception as e:
            # General exception handling, could be logging or re-raising
            raise Exception(
                "An unexpected error occurred while fetching network configuration: "
                + str(e)
            )

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

    def posixtime_to_min(self, timestamp):
        """Convert the given timestamp to minutes."""
        return timestamp / 60000

    def display_network_configuration(self):
        """Display the network information"""
        network_oracle_settings = self.get_network_configuration()

        configuration_details = f"""
    Contract address: {self.network_address}
    ########## C3 Network configuration ##########
    1. List of authorized nodes in Network: {len(network_oracle_settings.os_node_list)} nodes.
    2. The percentage of nodes needed for aggregation: {network_oracle_settings.os_updated_nodes/100}%.
    3. The max time since last node update for aggregation: {self.posixtime_to_min(network_oracle_settings.os_updated_node_time)} minutes.
    4. The min time since last aggregation for calculating a new network feed: {self.posixtime_to_min(network_oracle_settings.os_aggregate_time)} minutes.
    5. The percentage of change between last aggregated value and the new network feed: {network_oracle_settings.os_aggregate_change/100}%.
    6. Minimum Required Value for Recharging the C3 Pool: {network_oracle_settings.os_minimum_deposit} tokens.
    7. Valid time window to execute the aggregate transaction: {self.posixtime_to_min(network_oracle_settings.os_aggregate_valid_range)} minutes.
    """

        node, aggregate, platform = self.get_price_rewards(network_oracle_settings)
        rewards_details = f"""8. C3 Network rewards:
        8.1 Nodes: {node} C3
        8.2 Nodes: {aggregate} C3
        8.3 Platform: {platform} C3
    9. Consensus Setting (IQR): {network_oracle_settings.os_iqr_multiplier}.
    10. Consensus Setting (DP): {network_oracle_settings.os_divergence/100}%.
    """

        signatories, minimum_signatories = self.get_platform_signatories_info(
            network_oracle_settings
        )
        signatories_details = f"""11. Oracle platform entity:
        11.1 Signatories pool: {len(signatories)}
        11.2 Minimum number of signatories: {minimum_signatories}
    """

        print(configuration_details + rewards_details + signatories_details)
