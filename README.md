# Charli3 Network Feed Interaction Framework
Interact with Charli3 Network Feeds using Pycardano and Blockfrost.

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
# Features
* Retrieve exchange rates and timestamps directly from the Charli3 Network.
* Gain insights into network configurations and reward structures.
# Dependencies
Install dependencies using Poetry:
```
poetry install
```
# Setup
Ensure you have a `config.json` containing:

```
BLOCKFROST_PROJECT_ID: Your Blockfrost project ID.
BLOCKFROST_BASE_URL: The base URL for Blockfrost.
C3_CONTRACT_ADDRESS: Contract address for the C3 network.
MINTING_POLICY: Policy used for minting.
```
Initialize the [Blockfrost](https://blockfrost.io/) context using your project ID and base URL.

# Commands
To interact with this demo, use:

To obtain the C3 network Feed: `python network-feed/main.py preprod --feed`

To obtain the C3 netwrok Configuration: `python network-feed/main.py preprod --configuration`

For your convenience, the configuration file includes the configuration of the C3/ADA network feed. You can observe the C3 network in action on the [pre-production environment](https://preprod.cexplorer.io/address/addr_test1wr64gtafm8rpkndue4ck2nx95u4flhwf643l2qmg9emjajg2ww0nj/tx#data).
# Additional Details
## Datums Implementation

The provided code includes implementations for:

* Network feed data, using `PriceData` and `GenericData` classes.
* Network configurations, with classes like `OraclePlatform`, `PriceRewards`, and `OracleSettings`.
* An aggregate state, represented by the `AggState` and `AggDatum` classes.

## Charli3 Network Info Reader
The `Charli3NetworkInfoReader` class serves as the primary interface to read network details. It allows users to:

1. Fetch the oracle's exchange rate and creation and expiration timestamps.
3. Access the network's configuration (oracle settings).

 
# External Resources
To gain a better understanding of the Datum Standard structure, we recommend visiting:

1. [Datum Standard Lib](https://github.com/Charli3-Official/oracle-datum-lib) (PlutusTx).
2. [Datum Standard Documentation](https://docs.charli3.io/charli3s-documentation/oracle-feeds-datum-standard).
