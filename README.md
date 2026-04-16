# Charli3 Network Feed Interaction Framework
Interact with both legacy Charli3 network feeds and the newer Charli3 ODV contracts.

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

# Features
This repository now supports two contract families behind the same CLI:

* Legacy Charli3 feeds using `OracleFeed` and `AggState`.
* Charli3 ODV contracts using `C3AS`, `C3CS`, and `C3RA`.

The ODV flow is the main addition in this repo:

* `C3AS`: feed values live here. The reader filters out empty aggregate-state UTxOs and shows the valid ones sorted by creation time.
* `C3CS`: singleton core-settings UTxO. The reader parses and displays this configuration.
* `C3RA`: reward-account UTxOs. The reader parses all of them and shows them sorted by creation time.

# Dependencies
Install dependencies using Poetry:
```
poetry install
```

If you already have an older Poetry virtualenv for this project, resync it after pulling changes:
```
poetry install --sync
```

# Setup
Ensure you have a `config.yaml` containing the [Blockfrost](https://blockfrost.io/) or [Ogmios](https://github.com/CardanoSolutions/ogmios) and [Kupo](https://github.com/CardanoSolutions/kupo) configuration.

Network definitions live in `mainnet-c3-networks.yaml` and `preprod-c3-networks.yaml`.
ODV entries must include:
```
category: charli3-odv
```
Entries without `category` continue to use the legacy feed reader.

# Commands
To interact with this demo, use:
```
usage: python charli3 [-h] [--action {feed,configuration,all-configurations}] [--service {blockfrost,ogmios}] [token_pair] [{preprod,mainnet}]

Charli3 Network feed reader

positional arguments:
  token_pair            Token pair for the data feed
  {preprod,mainnet}     Environment to use

options:
  -h, --help            show this help message and exit
  --action {feed,configuration,all-configurations}
                        Retrieve the oracle feed for the specified token pair
  --service {blockfrost,ogmios}
                        External service to read blockhain information

Copyright: (c) 2020 - 2024 Charli3
```

For convenience, the repo already includes network definitions in `mainnet-c3-networks.yaml` and `preprod-c3-networks.yaml`.

Legacy example:
```
poetry run charli3 --action feed --service blockfrost ADA-CHARLI3 mainnet
```

Legacy Ogmios example:
```
poetry run charli3 --action feed --service ogmios ADA-CHARLI3 preprod
```

ODV feed example:
```
poetry run charli3 --action feed --service blockfrost USDM-RESERVES mainnet
```

ODV configuration example:
```
poetry run charli3 --action configuration --service blockfrost USDM-RESERVES mainnet
```

ODV preprod example:
```
poetry run charli3 --action feed --service blockfrost JOSE-USD preprod
```

# Additional Details
## Datums Implementation

The provided code includes implementations for:

* Legacy oracle price information using `PriceData` and `GenericData`.
* Legacy network configuration datums using `OraclePlatform`, `PriceRewards`, and `OracleSettings`.
* ODV core-settings datums using `OracleSettingsDatum` and `OracleSettingsVariant`.
* ODV reward-account datums using `RewardAccountsDatum`.

## ODV Notes

The ODV reader intentionally keeps the legacy path unchanged and only switches behavior when `category: charli3-odv` is present in the network definition.

For ODV contracts:

* `feed` shows valid `C3AS` rows only, filtered to exclude empty datums.
* feed values are displayed scaled by `1e6`.
* `configuration` and `all-configurations` show the singleton `C3CS` plus every parsed `C3RA`.

# External Resources
To gain a better understanding of the Datum Standard structure, we recommend visiting:

1. [Datum Standard Lib](https://github.com/Charli3-Official/oracle-datum-lib) (PlutusTx).
2. [Datum Standard Documentation](https://docs.charli3.io/charli3s-documentation/oracle-feeds-datum-standard).
