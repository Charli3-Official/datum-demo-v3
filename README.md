# Charli3 Network Feed Interaction Framework
Interact with Charli3 Network Feeds

# Table of Contents

1. [Charli3 Network Feed Interaction Framework](#charli3-network-feed-interaction-framework)
    - [Features](#features)
    - [Dependencies](#dependencies)
    - [Setup](#setup)
    - [Commands](#commands)
    - [Additional Details](#additional-details)
        * [Datums Implementation](#datums-implementation)
        * [Charli3 Network Info Reader](#charli3-network-info-reader)
    - [External Resources](#external-resources)

# Dependencies
Install dependencies using Poetry:
```
poetry install
```
# Setup
Ensure you have a `config.json` containing the [Blockfrost](https://blockfrost.io/) or [Demeter](https://demeter.run/) configuration.

# Commands
To interact with this demo, use:
```
python charli3 [-h] [--action {feed,configuration}] [--service {blockfrost,demeter}] [token_pair] [{preprod,mainnet}]
```

For your convenience, the configuration file includes lives oracle networks under `mainnet-c3-networkds.yaml` and `preprod-c3-networks`

# Additional Details
## Datums Implementation

The provided code includes implementations for:

* Oracle price information using `PriceData` and `GenericData` classes.
* Network configurations with classes like `OraclePlatform`, `PriceRewards`, and `OracleSettings`.

**Note**: Blockfrost configuration fails decoding Datum types, we are searching for a solution.
# External Resources
To gain a better understanding of the Datum Standard structure, we recommend visiting:

1. [Datum Standard Lib](https://github.com/Charli3-Official/oracle-datum-lib) (PlutusTx).
2. [Datum Standard Documentation](https://docs.charli3.io/charli3s-documentation/oracle-feeds-datum-standard).
