# Charli3 Network Feed Interaction Framework
Effortlessly Interact with Charli3 Network Feeds using Pycardano and Blockfrost.

Fully Compatible with C3 Networks Version 3
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
* Access both the creation and expiration times of the feeds.
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
The configuration file is loaded at runtime, and environment variables are set accordingly.

Initialize the Blockfrost context using your project ID and base URL.

Use the `Charli3NetworkInfoReader` class to read and process data from the C3 network.

# Commands
To run the program in a live environment, use:
```bash
python network-feed-demo/main.py
Available sub-commands:

c3-network:
--configuration: Displays the C3 Network's configuration.
--feed: Provides detailed feed information.
```
# Additional Details
## Datums Implementation

The provided code includes implementations for:

* Network feed data, using `PriceData` and `GenericData` classes.
* Network configurations, with classes like `OraclePlatform`, `PriceRewards`, and `OracleSettings`.
* An aggregate state, represented by the `AggState` and `AggDatum` classes.

## Charli3 Network Info Reader
The Charli3NetworkInfoReader class serves as the primary interface to read network details. It allows users to:

1. Fetch the oracle's exchange rate.
2. Retrieve the feed's creation and expiration timestamps.
3. Access the network's configuration.
4. Obtain reward information based on OracleSettings.
5. Understand platform signatories' details.
 
# External Resources
To gain a better understanding of the Datum Standard structure, we recommend visiting:

1. [Datum Standard Lib](https://github.com/Charli3-Official/oracle-datum-lib) (PlutusTx) on GitHub
2. Network Feeds [Datum Standard Documentation](https://docs.charli3.io/charli3s-documentation/oracle-feeds-datum-standard)
