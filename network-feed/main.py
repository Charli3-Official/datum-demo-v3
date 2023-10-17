"""
Key Framework for Interacting with Charli3 Network Feeds
"""
import argparse
import json
import sys

from datetime import datetime
from charli3_network_info_reader import Charli3NetworkInfoReader
from pycardano import BlockFrostChainContext, Address


# Load configuration from JSON file
CONFIG_FILE = "config.json"

try:
    with open(CONFIG_FILE, "r", encoding="UTF-8") as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"Configuration file '{CONFIG_FILE}' not found.")
    sys.exit(1)

# Environment variables
BLOCKFROST_PROJECT_ID = config.get("BLOCKFROST_PROJECT_ID", "")
BLOCKFROST_BASE_URL = config.get("BLOCKFROST_BASE_URL", "")

# Blockfrost's context
CONTEXT = BlockFrostChainContext(
    project_id=BLOCKFROST_PROJECT_ID, base_url=BLOCKFROST_BASE_URL
)

# Contract information
C3_CONTRACT_ADDRESS = Address.from_primitive(config.get("C3_CONTRACT_ADDRESS"))
NFT_MINTING_POLICY = config.get("MINTING_POLICY")

# Instantiate the 'Charli3NetworkInfoReader' class for data retrieval
read = Charli3NetworkInfoReader(C3_CONTRACT_ADDRESS, NFT_MINTING_POLICY, CONTEXT)

# ------------------------------#
#         Parser Section        #
# ------------------------------#


def create_parser():
    """Initialize and return the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="python network-feed-demo/main.py",
        description="Charli3 Network feed reader (PREPRODUCTION)",
        epilog="Copyright: (c) 2020 - 2023 Charli3",
    )
    add_subparsers(parser)
    return parser


def add_subparsers(parser):
    """Add subparsers for the main parser."""
    subparsers = parser.add_subparsers(dest="command")

    c3_network_parser = subparsers.add_parser(
        "c3-network",
        help="C3 Network Reader",
        description="Available C3 network interactions",
    )

    action_group = c3_network_parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--configuration",
        action="store_true",
        help="C3 Network configuration",
    )
    action_group.add_argument(
        "--feed",
        action="store_true",
        help="C3 Network feed",
    )


def format_timestamp(timestamp):
    """Convert the given timestamp to a human-readable datetime string."""
    # Divide to convert from milliseconds to seconds
    return datetime.utcfromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")


def posixtime_to_min(timestamp):
    """Convert the given timestamp to minutes."""
    return timestamp / 60000


def display_feed_info():
    """Display the feed information."""
    # Exchange rate
    exchange_rate = read.get_oracle_exchange_rate()
    exchange_rate_decimal = exchange_rate / 1000000

    # Creation time
    generation_time = format_timestamp(read.get_network_timestamp())

    # Expiration time
    expiration_time = format_timestamp(read.get_network_expiration())

    print(f"Contract address: {read.network_address}")
    print(f"C3 Network feed [USD/ADA]: {exchange_rate_decimal}")
    print(f"Creation time: {generation_time}")
    print(f"Expiration time: {expiration_time}")


def display_network_configuration():
    """Display the network information"""
    network_oracle_settings = read.get_network_configuration()

    print(f"Contract address: {read.network_address}")
    print("########## C3 Network configuration [USD/ADA] ##########")
    print(
        "1. List of autorized nodes in Network: "
        f"{len(network_oracle_settings.os_node_list)} nodes."
    )
    print(
        "2. The percentage of nodes needed for aggregation: "
        f"{network_oracle_settings.os_updated_nodes/100}%."
    )
    print(
        "3. The max time since last node update for aggregation: "
        f"{posixtime_to_min(network_oracle_settings.os_updated_node_time)} "
        "minutes."
    )
    print(
        "4. The min time since last aggregation for calculating a new network "
        f"feed: {posixtime_to_min(network_oracle_settings.os_aggregate_time)} "
        "minutes."
    )
    print(
        "5. The percentage of change between last aggregated value and the "
        f"new network feed: {network_oracle_settings.os_aggregate_change/100}%."
    )
    print(
        "6. Minimum Required Value for Recharging the C3 Pool: "
        f"{network_oracle_settings.os_minimum_deposit} tokens."
    )
    print(
        "7. Valid time window to execute the aggregate transaction: "
        f"{posixtime_to_min(network_oracle_settings.os_aggregate_valid_range)} "
        "minutes."
    )

    node, aggregate, platform = read.get_price_rewards(network_oracle_settings)
    print(
        f"""8. C3 Network rewards:
    8.1 Nodes: {node} C3
    8.2 Nodes: {aggregate} C3
    8.3 Platform: {platform} C3"""
    )

    print(
        "9. Threshold setting 1 for Consensus (IQR): "
        f"{network_oracle_settings.os_iqr_multiplier}."
    )
    print(
        "10. Threshold setting 2 for Consensus (DIV): "
        f"{network_oracle_settings.os_divergence/100}%."
    )

    signatories, minimum_signatories = read.get_platform_signatories_info(
        network_oracle_settings
    )
    print(
        f"""11. Oracle platform entity:
    11.1 Signatories pool: {len(signatories)}
    11.2 Minimum number of signatories: {minimum_signatories}"""
    )


def process_arguments(args):
    """Process and act based on the given command-line arguments."""
    if args.command == "c3-network":
        if args.configuration:
            display_network_configuration()
        elif args.feed:
            display_feed_info()


def main():
    """main execution program"""

    parser = create_parser()
    args = parser.parse_args()
    process_arguments(args)


if __name__ == "__main__":
    main()
