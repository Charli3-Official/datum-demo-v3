"""
Datums implementation
To gain a better understanding of the Datum Standard structure, we recommend
visiting: https://github.com/Charli3-Official/oracle-datum-lib
and
https://docs.charli3.io/charli3s-documentation/oracle-feeds-datum-standard
"""

from dataclasses import dataclass
from typing import Union

from pycardano import PlutusData
from pycardano.serialization import IndefiniteList


# ------------------------------#
#         Network Feed          #
# ------------------------------#


# Network feed
@dataclass
class PriceData(PlutusData):
    """Represents cip oracle datum PriceMap(Tag +2)"""

    CONSTR_ID = 2
    price_map: dict

    def get_price(self) -> int:
        """get price from price map"""
        return self.price_map[0]

    def get_timestamp(self) -> int:
        """get timestamp of the feed"""
        return self.price_map[1]

    def get_expiry(self) -> int:
        """get expiry of the feed"""
        return self.price_map[2]


@dataclass
class GenericData(PlutusData):
    """Oracle Datum"""

    CONSTR_ID = 0
    price_data: PriceData


# ------------------------------#
#     Network Configurations    #
# ------------------------------#


@dataclass
class OraclePlatform(PlutusData):
    """Oracle Platform parameters"""

    CONSTR_ID = 0
    pmultisig_pkhs: IndefiniteList  # Allowed pkhs for platform authorization
    pmultisig_threshold: int  # required number of signatories for authorization


@dataclass
class PriceRewards(PlutusData):
    """Node Fee parameters"""

    CONSTR_ID = 0
    node_fee: int  # Individual node reward for aggregation participation.
    aggregate_fee: int  # Node compensatoin for execution of the
    # aggregation transaction.
    platform_fee: int  # Platform compensation for maintenance systems.


@dataclass
class OracleSettings(PlutusData):
    """Oracle Settings parameters"""

    CONSTR_ID = 0
    os_node_list: IndefiniteList  # The list of autorized nodes'
    # public key hashes
    os_updated_nodes: int  # The percentage of nodes needed for aggregation
    os_updated_node_time: int  # The max time since last node update for
    # aggregation (in milliseconds)
    os_aggregate_time: int  # The min time since last aggregation for
    # calculating a new one (in milliseconds)
    os_aggregate_change: int  # The percentage of change between last
    # aggregated value and the new one
    os_minimum_deposit: int  # Minimum value required for topping up the
    # aggregate UTxO (1*10^9).
    os_aggregate_valid_range: int  # Valid time window to execute the
    # aggregate transaction (600000, 10min)
    os_node_fee_price: PriceRewards  # Rewards
    os_iqr_multiplier: int  # Threshold setting 1 for Consensus:
    # Interquartile Range (0 - N).
    os_divergence: int  # Threshold setting 2 for Consensus:
    # Divergence in Percentage
    os_platform: OraclePlatform  # Oracle platform entity


@dataclass
class AggState(PlutusData):
    """Agg State parameters"""

    CONSTR_ID = 0
    ag_settings: OracleSettings


@dataclass
class AggDatum(PlutusData):
    """Agg Datum"""

    CONSTR_ID = 2
    aggstate: AggState


# ------------------------------#
#         Charli3 ODV           #
# ------------------------------#


AssetName = bytes
PolicyId = bytes
PosixTimeDiff = int
ScriptHash = bytes


@dataclass
class NoDatum(PlutusData):
    """Universal None type for ODV PlutusData."""

    CONSTR_ID = 1


@dataclass
class RewardPrices(PlutusData):
    """Reward price configuration for ODV settings."""

    CONSTR_ID = 0
    node_fee: int
    platform_fee: int


@dataclass
class Asset(PlutusData):
    """Native token asset."""

    CONSTR_ID = 0
    policy_id: PolicyId
    name: AssetName


@dataclass
class SomeAsset(PlutusData):
    """Optional asset wrapper."""

    CONSTR_ID = 0
    asset: Asset


FeeRateNFT = Union[SomeAsset, NoDatum]


@dataclass
class FeeConfig(PlutusData):
    """Fee configuration embedded in ODV core settings."""

    CONSTR_ID = 0
    rate_nft: FeeRateNFT
    reward_prices: RewardPrices


@dataclass
class SomePosixTime(PlutusData):
    """Optional POSIX time wrapper."""

    CONSTR_ID = 0
    value: int


@dataclass
class OracleSettingsDatum(PlutusData):
    """Mutable ODV core settings datum."""

    CONSTR_ID = 0
    nodes: IndefiniteList
    required_node_signatures_count: int
    fee_info: FeeConfig
    aggregation_liveness_period: PosixTimeDiff
    time_uncertainty_aggregation: PosixTimeDiff
    time_uncertainty_platform: PosixTimeDiff
    iqr_fence_multiplier: int
    median_divergency_factor: int
    utxo_size_safety_buffer: int
    pause_period_started_at: Union[SomePosixTime, NoDatum]


@dataclass
class OracleSettingsVariant(PlutusData):
    """ODV oracle settings variant."""

    CONSTR_ID = 1
    datum: OracleSettingsDatum


@dataclass
class RewardAccounts(PlutusData):
    """Reward account balances grouped by node PKH with a creation time."""

    CONSTR_ID = 0
    account_rewards: dict
    created_at: int


@dataclass
class RewardAccountsDatum(PlutusData):
    """Top-level ODV reward-account datum."""

    CONSTR_ID = 2
    reward_accounts: RewardAccounts
