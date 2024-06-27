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
    
The following demo was tested with cardano-node v8.9.3, Ogmios v6.4.0, and Kupo v2.8.0.

# Dependencies
Install dependencies using Poetry:
```
poetry install
```
# Setup
Ensure you have a `config.json` containing the [Blockfrost](https://blockfrost.io/) or [Ogmios](https://github.com/CardanoSolutions/ogmios) and [Kupo](https://github.com/CardanoSolutions/kupo) configuration.

# Commands
To interact with this demo, use:
```
usage: python charli3 [-h] [--action {feed,configuration}] [--service {blockfrost,ogmios}] [token_pair] [{preprod,mainnet}]

Charli3 Network feed reader

positional arguments:
  token_pair            Token pair for the data feed
  {preprod,mainnet}     Environment to use

options:
  -h, --help            show this help message and exit
  --action {feed,configuration}
                        Retrieve the oracle feed for the specified token pair
  --service {blockfrost,ogmios}
                        External service to read blockhain information

Copyright: (c) 2020 - 2024 Charli3```

For your convenience, the configuration file includes lives oracle networks under `mainnet-c3-networkds.yaml` and `preprod-c3-networks`

```
For example:
```
poetry run charli3 --action feed --service blockfrost ADA-CHARLI3 mainnet
```
Or
```
poetry run charli3 --action feed --service ogmios ADA-CHARLI3 preprod
```

# Additional Details
## Datums Implementation

The provided code includes implementations for:

* Oracle price information using `PriceData` and `GenericData` classes.
* Network configurations with classes like `OraclePlatform`, `PriceRewards`, and `OracleSettings`.

# External Resources
To gain a better understanding of the Datum Standard structure, we recommend visiting:

1. [Datum Standard Lib](https://github.com/Charli3-Official/oracle-datum-lib) (PlutusTx).
2. [Datum Standard Documentation](https://docs.charli3.io/charli3s-documentation/oracle-feeds-datum-standard).
