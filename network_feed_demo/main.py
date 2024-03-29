""" Key Framework for Interacting with Charli3 Network Feeds """

import argparse
import yaml
import sys

from pycardano import BlockFrostChainContext, OgmiosChainContext, Address
from .charli3_network_info_reader import Charli3NetworkInfoReader

def create_parser():
    """Initialize and return the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="python charli3",
        description="Charli3 Network feed reader",
        epilog="Copyright: (c) 2020 - 2024 Charli3",
    )
    add_arguments(parser)
    return parser


def add_arguments(parser):
    """Add subparsers for the main parser."""
    parser.add_argument("token_pair", nargs='?', default = "ADA-USD", help="Token pair for the data feed")
    parser.add_argument("environment", nargs='?', default = "preprod", choices = ["preprod", "mainnet"], help="Environment to use")

    parser.add_argument("--action", choices = ["feed", "configuration"], default = "feed", help="Retrieve the oracle feed for the specified token pair", )
    parser.add_argument("--service", choices = ["blockfrost", "demeter"], default = "blockfrost", help="External service to read blockhain information")
    return parser

def load_config():
    """Loads the YAML configuration file."""
    try:
        with open("config.yaml", "r", encoding="UTF-8") as config_yaml:
            return yaml.load(config_yaml, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print("Configuration file not found.")
        sys.exit(1)

def validate_config(config, service, required_keys):
    """Validates that all required keys exist for a service configuration."""
    if service not in config or not all(key in config[service] for key in required_keys):
        raise ValueError(f"Context for {service} not found or is incomplete.")

def context(args):
    """Connection context"""
    configyaml = load_config()

    if args.service == "blockfrost":
        required_keys = ["project_id", "base_url"]
        validate_config(configyaml, args.service, required_keys)

        return BlockFrostChainContext(
            project_id=configyaml[args.service].get("project_id", ""),
            base_url=configyaml[args.service].get("base_url", "")
        )
    elif args.service == "demeter":
        required_keys = ["kupo", "ogmios"]
        validate_config(configyaml, args.service, required_keys)

        return OgmiosChainContext(
            configyaml[args.service].get("ogmios", ""),
            args.environment,
            configyaml[args.service].get("kupo", ""),
        )
    else:
        raise ValueError(f"Service {args.service} is not supported.")

def display(args):
    """Display the C3 network information"""
    try:
        with open(f"{args.environment}-c3-networks.yaml", "r", encoding="UTF-8") as c3_networks_yaml:
           c3_networks = yaml.load(c3_networks_yaml, Loader=yaml.FullLoader)
    except FileNotFoundError:
        sys.exit(1)
    if args.token_pair not in c3_networks or ('address' not in c3_networks[args.token_pair] or 'minting-policy' not in c3_networks[args.token_pair]):
        raise ValueError(f"Token pair {args.token_pair} not found in the network.")

    address = Address.from_primitive(c3_networks.get(args.token_pair).get('address'))
    minting_policy = c3_networks.get(args.token_pair)['minting-policy']

    reader = Charli3NetworkInfoReader(address, minting_policy, context(args))

    if args.action != "feed":
        reader.display_network_configuration()
    reader.display_oracle_feed()

def main():
    """main execution program"""
    parser = create_parser()
    args = parser.parse_args(None if sys.argv[1:] else ["-h"])
    display(args)

if __name__ == "__main__":
    main()
