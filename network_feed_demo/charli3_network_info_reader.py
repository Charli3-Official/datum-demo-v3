"""Read C3 network configuration and feed information."""

from datetime import datetime

from pycardano import Address, MultiAsset
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .datums import (
    AggDatum,
    GenericData,
    OraclePlatform,
    OracleSettings,
    OracleSettingsVariant,
    RewardAccountsDatum,
)

console = Console()


class Charli3NetworkInfoReader:
    """
    Charli3 network information reader.

    Supports the legacy `OracleFeed` / `AggState` contracts and the new
    `charli3-odv` contracts that use `C3AS`, `C3CS`, and `C3RA`.
    """

    def __init__(
        self,
        network_address: Address,
        minting_policy: str,
        context,
        category: str = "charli3-network-feed",
    ):
        self.network_address = network_address
        self.category = category
        self.aggregate_state_nft = MultiAsset.from_primitive(
            {minting_policy: {b"AggState": 1}}
        )
        self.network_feed_nft = MultiAsset.from_primitive(
            {minting_policy: {b"OracleFeed": 1}}
        )
        self.odv_aggregate_state_nft = MultiAsset.from_primitive(
            {minting_policy: {b"C3AS": 1}}
        )
        self.odv_core_settings_nft = MultiAsset.from_primitive(
            {minting_policy: {b"C3CS": 1}}
        )
        self.odv_reward_accounts_nft = MultiAsset.from_primitive(
            {minting_policy: {b"C3RA": 1}}
        )
        self.context = context

    def is_odv(self):
        """Whether the current contract uses the ODV datum layout."""
        return self.category == "charli3-odv"

    def format_timestamp(self, timestamp):
        """Convert epoch milliseconds to UTC string."""
        return datetime.utcfromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")

    def posixtime_to_min(self, timestamp):
        """Convert POSIX time in milliseconds to minutes."""
        return timestamp / 60000

    def get_contract_utxos(self):
        """Fetch all UTxOs at the configured contract address."""
        return self.context.utxos(str(self.network_address))

    def utxo_has_asset(self, utxo, asset: MultiAsset):
        """Check whether a UTxO contains the requested NFT."""
        multi_asset = utxo.output.amount.multi_asset
        return bool(multi_asset and multi_asset >= asset)

    def format_key_hash(self, key_hash):
        """Render bytes-like key hashes consistently."""
        if hasattr(key_hash, "to_primitive"):
            primitive = key_hash.to_primitive()
            return primitive.hex() if isinstance(primitive, bytes) else str(primitive)
        return key_hash.hex() if isinstance(key_hash, bytes) else str(key_hash)

    def parse_feed_datum(self, datum_cbor):
        """Parse the shared feed datum used by legacy and ODV aggregate states."""
        return GenericData.from_cbor(datum_cbor)

    def get_valid_odv_feed_entries(self):
        """Fetch non-empty ODV aggregate-state UTxOs sorted by creation time."""
        feed_entries = []

        for utxo in self.get_contract_utxos():
            if not self.utxo_has_asset(utxo, self.odv_aggregate_state_nft):
                continue

            datum = getattr(utxo.output, "datum", None)
            if not datum or not getattr(datum, "cbor", None):
                continue

            try:
                parsed_datum = self.parse_feed_datum(datum.cbor)
                price_data = parsed_datum.price_data
                if not all(
                    (
                        price_data.get_price(),
                        price_data.get_timestamp(),
                        price_data.get_expiry(),
                    )
                ):
                    continue
                feed_entries.append((price_data.get_timestamp(), parsed_datum, utxo))
            except Exception:
                # Empty ODV C3AS placeholders do not decode as full price data.
                continue

        feed_entries.sort(key=lambda item: item[0])
        return feed_entries

    def get_odv_core_settings(self):
        """Fetch the singleton ODV core-settings datum."""
        core_settings_utxo = next(
            (
                utxo
                for utxo in self.get_contract_utxos()
                if self.utxo_has_asset(utxo, self.odv_core_settings_nft)
            ),
            None,
        )

        if not core_settings_utxo:
            raise ValueError("No C3CS UTxO found for this ODV contract.")

        datum = getattr(core_settings_utxo.output, "datum", None)
        if not datum or not getattr(datum, "cbor", None):
            raise ValueError("The C3CS UTxO does not contain an inline datum.")

        return OracleSettingsVariant.from_cbor(datum.cbor).datum, core_settings_utxo

    def get_odv_reward_account_entries(self):
        """Fetch all ODV reward-account UTxOs sorted by creation time."""
        reward_entries = []

        for utxo in self.get_contract_utxos():
            if not self.utxo_has_asset(utxo, self.odv_reward_accounts_nft):
                continue

            datum = getattr(utxo.output, "datum", None)
            if not datum or not getattr(datum, "cbor", None):
                continue

            reward_accounts = RewardAccountsDatum.from_cbor(datum.cbor).reward_accounts
            reward_entries.append((reward_accounts.created_at, reward_accounts, utxo))

        reward_entries.sort(key=lambda item: item[0])
        return reward_entries

    def display_odv_oracle_feed(self):
        """Display all valid ODV aggregate-state feed UTxOs."""
        feed_entries = self.get_valid_odv_feed_entries()
        if not feed_entries:
            raise ValueError("No non-empty C3AS UTxOs found for this ODV contract.")

        feeds_table = Table(
            title="📊 CHARLI3 ODV - Aggregate States",
            show_header=True,
        )
        feeds_table.add_column("Index", style="cyan")
        feeds_table.add_column("Creation Time", style="green")
        feeds_table.add_column("Expiration Time", style="yellow")
        feeds_table.add_column("Feed Value", style="bold cyan")
        feeds_table.add_column("Output Index", style="magenta")

        for idx, (_, datum, utxo) in enumerate(feed_entries, start=1):
            feeds_table.add_row(
                str(idx),
                self.format_timestamp(datum.price_data.get_timestamp()),
                self.format_timestamp(datum.price_data.get_expiry()),
                f"{float(datum.price_data.get_price()) / 1000000:.6f}",
                str(utxo.input.index),
            )

        console.print(Panel(feeds_table, border_style="blue", padding=(1, 2)))

    def display_odv_network_configuration(self):
        """Display the ODV core settings and all reward-account snapshots."""
        network_settings, _ = self.get_odv_core_settings()
        reward_entries = self.get_odv_reward_account_entries()

        config_table = Table(title="⚙️  CHARLI3 ODV - Core Settings", show_header=False)
        config_table.add_row("Contract Address:", Text(str(self.network_address), style="cyan"))
        config_table.add_row(
            "Authorized Nodes:",
            Text(str(len(network_settings.nodes)), style="green"),
        )
        config_table.add_row(
            "Required Signatures:",
            Text(str(network_settings.required_node_signatures_count), style="magenta"),
        )
        config_table.add_row(
            "Aggregation Liveness:",
            Text(
                f"{self.posixtime_to_min(network_settings.aggregation_liveness_period):.1f} min",
                style="yellow",
            ),
        )
        config_table.add_row(
            "Aggregation Uncertainty:",
            Text(
                f"{self.posixtime_to_min(network_settings.time_uncertainty_aggregation):.1f} min",
                style="yellow",
            ),
        )
        config_table.add_row(
            "Platform Uncertainty:",
            Text(
                f"{self.posixtime_to_min(network_settings.time_uncertainty_platform):.1f} min",
                style="yellow",
            ),
        )
        config_table.add_row(
            "IQR Fence Multiplier:",
            Text(str(network_settings.iqr_fence_multiplier), style="cyan"),
        )
        config_table.add_row(
            "Median Divergency Factor:",
            Text(
                f"{network_settings.median_divergency_factor/1000:.3f}",
                style="cyan",
            ),
        )
        config_table.add_row(
            "UTxO Size Safety Buffer:",
            Text(str(network_settings.utxo_size_safety_buffer), style="green"),
        )
        config_table.add_row(
            "Node Fee:",
            Text(str(network_settings.fee_info.reward_prices.node_fee), style="bold green"),
        )
        config_table.add_row(
            "Platform Fee:",
            Text(
                str(network_settings.fee_info.reward_prices.platform_fee),
                style="bold green",
            ),
        )

        console.print(Panel(config_table, border_style="green", padding=(1, 2)))

        nodes_table = Table(title="🧾 CHARLI3 ODV - Node Registry", show_header=True)
        nodes_table.add_column("Node PKH", style="cyan")

        for node_pkh in sorted(
            network_settings.nodes,
            key=self.format_key_hash,
        ):
            nodes_table.add_row(self.format_key_hash(node_pkh))

        console.print(Panel(nodes_table, border_style="blue", padding=(1, 2)))

        rewards_summary = Table(
            title="💰 CHARLI3 ODV - Reward Accounts",
            show_header=True,
        )
        rewards_summary.add_column("Index", style="cyan")
        rewards_summary.add_column("Creation Time", style="green")
        rewards_summary.add_column("Accounts", style="magenta")
        rewards_summary.add_column("Total Reward", style="bold cyan")
        rewards_summary.add_column("Output Index", style="yellow")

        for idx, (created_at, reward_accounts, utxo) in enumerate(reward_entries, start=1):
            rewards_summary.add_row(
                str(idx),
                self.format_timestamp(created_at),
                str(len(reward_accounts.account_rewards)),
                str(sum(reward_accounts.account_rewards.values())),
                str(utxo.input.index),
            )

        console.print(Panel(rewards_summary, border_style="cyan", padding=(1, 2)))

        for idx, (created_at, reward_accounts, _) in enumerate(reward_entries, start=1):
            accounts_table = Table(
                title=f"Reward Snapshot #{idx} - {self.format_timestamp(created_at)}",
                show_header=True,
            )
            accounts_table.add_column("Node PKH", style="cyan")
            accounts_table.add_column("Reward", style="bold green")

            for node_pkh, reward in sorted(
                reward_accounts.account_rewards.items(),
                key=lambda item: self.format_key_hash(item[0]),
            ):
                accounts_table.add_row(self.format_key_hash(node_pkh), str(reward))

            console.print(Panel(accounts_table, border_style="magenta", padding=(1, 2)))

    def display_oracle_feed(self):
        """Get the oracle feed exchange rate."""
        if self.is_odv():
            try:
                self.display_odv_oracle_feed()
            except ValueError as exc:
                console.print(f"[red]Error retrieving oracle feed: {exc}[/red]")
            except Exception as exc:
                console.print(
                    f"[red]Error retrieving oracle feed: {type(exc).__name__}: {exc}[/red]"
                )
            return

        try:
            oracle_utxos = self.get_contract_utxos()

            oracle_feed_utxo = next(
                (
                    utxo
                    for utxo in oracle_utxos
                    if self.utxo_has_asset(utxo, self.network_feed_nft)
                ),
                None,
            )

            if not oracle_feed_utxo:
                raise ValueError(
                    "No Oracle Feed UTXO found matching the network feed NFT."
                )

            try:
                datum = oracle_feed_utxo.output.datum
                datum_type = type(datum).__name__
                console.print(f"[dim]Datum type: {datum_type}[/dim]")

                if datum and not isinstance(datum, AggDatum):
                    if hasattr(datum, "cbor") and datum.cbor:
                        oracle_inline_datum = self.parse_feed_datum(datum.cbor)

                        price = float(oracle_inline_datum.price_data.get_price()) / 1000000
                        creation_time = self.format_timestamp(
                            oracle_inline_datum.price_data.get_timestamp()
                        )
                        expiration_time = self.format_timestamp(
                            oracle_inline_datum.price_data.get_expiry()
                        )

                        table = Table(title="📊 CHARLI3 - Oracle Feed", show_header=False)
                        table.add_row(
                            "Last Price:", Text(f"${price:.6f}", style="bold cyan")
                        )
                        table.add_row(
                            "Creation Time:", Text(creation_time, style="green")
                        )
                        table.add_row(
                            "Expiration Time:", Text(expiration_time, style="yellow")
                        )

                        panel = Panel(table, border_style="blue", padding=(1, 2))
                        console.print(panel)
            except Exception as datum_error:
                console.print(
                    f"[red]Error parsing datum: {type(datum_error).__name__}: {datum_error}[/red]"
                )
                raise

        except ValueError as exc:
            console.print(f"[red]Error retrieving oracle feed: {exc}[/red]")
        except Exception as exc:
            console.print(
                f"[red]Error retrieving oracle feed: {type(exc).__name__}: {exc}[/red]"
            )

    def get_all_network_configurations(self):
        """Fetch all legacy aggregate UTxO configurations."""
        try:
            aggregate_utxos = []
            for utxo in self.get_contract_utxos():
                if self.utxo_has_asset(utxo, self.aggregate_state_nft):
                    try:
                        aggregate_state_inline_datum = AggDatum.from_cbor(
                            utxo.output.datum.cbor
                        )
                        aggregate_utxos.append(
                            (
                                utxo.input.transaction_id,
                                aggregate_state_inline_datum.aggstate.ag_settings,
                                utxo,
                            )
                        )
                    except Exception as exc:
                        console.print(
                            f"[yellow]Warning: Failed to parse aggregate UTxO: {exc}[/yellow]"
                        )

            if not aggregate_utxos:
                raise ValueError("No matching Aggregate State UTxOs found.")

            aggregate_utxos.sort(key=lambda item: str(item[0]))
            return aggregate_utxos

        except ValueError as exc:
            raise ValueError("Failed to fetch network configurations: " + str(exc))
        except Exception as exc:
            raise Exception(
                "An unexpected error occurred while fetching network configurations: "
                + str(exc)
            ) from exc

    def get_network_configuration(self):
        """Fetch the most recent legacy aggregate UTxO configuration."""
        try:
            aggregate_utxos = self.get_all_network_configurations()
            return aggregate_utxos[-1][1]

        except (ValueError, IndexError) as exc:
            raise ValueError("Failed to fetch network configuration: " + str(exc))
        except Exception as exc:
            raise Exception(
                "An unexpected error occurred while fetching network configuration: "
                + str(exc)
            ) from exc

    def get_price_rewards(self, rewards: OracleSettings):
        """Get price rewards from a legacy OracleSettings datum."""
        return (
            rewards.os_node_fee_price.node_fee,
            rewards.os_node_fee_price.aggregate_fee,
            rewards.os_node_fee_price.platform_fee,
        )

    def get_platform_signatories_info(self, platform: OraclePlatform):
        """Get legacy platform signatories information."""
        return (
            platform.os_platform.pmultisig_pkhs,
            platform.os_platform.pmultisig_threshold,
        )

    def display_all_network_configurations(self):
        """Display all network configurations."""
        if self.is_odv():
            self.display_odv_network_configuration()
            return

        aggregate_utxos = self.get_all_network_configurations()

        utxos_table = Table(
            title="📋 All Aggregate State UTxOs (Sorted by Creation Time)",
            show_header=True,
        )
        utxos_table.add_column("Index", style="cyan")
        utxos_table.add_column("Transaction ID", style="magenta")
        utxos_table.add_column("Output Index", style="yellow")

        for idx, (tx_id, _, utxo) in enumerate(aggregate_utxos):
            utxos_table.add_row(
                str(idx + 1),
                str(tx_id)[:16] + "...",
                str(utxo.input.index),
            )

        console.print(Panel(utxos_table, border_style="cyan", padding=(1, 2)))

        for idx, (tx_id, settings, utxo) in enumerate(aggregate_utxos):
            console.print(f"\n[bold blue]Configuration #{idx + 1}[/bold blue]")
            config_table = Table(show_header=False)
            config_table.add_row("Transaction:", Text(str(tx_id)[:32] + "...", style="cyan"))
            config_table.add_row("Output Index:", Text(str(utxo.input.index), style="yellow"))
            config_table.add_row(
                "Authorized Nodes:", Text(str(len(settings.os_node_list)), style="green")
            )
            config_table.add_row(
                "Aggregation Threshold:",
                Text(f"{settings.os_updated_nodes/100:.1f}%", style="magenta"),
            )
            config_table.add_row(
                "Max Node Update Time:",
                Text(
                    f"{self.posixtime_to_min(settings.os_updated_node_time):.1f} min",
                    style="yellow",
                ),
            )
            config_table.add_row(
                "Min Aggregation Time:",
                Text(
                    f"{self.posixtime_to_min(settings.os_aggregate_time):.1f} min",
                    style="yellow",
                ),
            )

            console.print(Panel(config_table, border_style="green", padding=(1, 2)))

    def display_network_configuration(self):
        """Display the most recent network configuration."""
        if self.is_odv():
            self.display_odv_network_configuration()
            return

        network_oracle_settings = self.get_network_configuration()

        config_table = Table(title="⚙️  C3 Network Configuration", show_header=False)
        config_table.add_row("Contract Address:", Text(str(self.network_address), style="cyan"))
        config_table.add_row(
            "Authorized Nodes:",
            Text(str(len(network_oracle_settings.os_node_list)), style="green"),
        )
        config_table.add_row(
            "Aggregation Threshold:",
            Text(f"{network_oracle_settings.os_updated_nodes/100:.1f}%", style="magenta"),
        )
        config_table.add_row(
            "Max Node Update Time:",
            Text(
                f"{self.posixtime_to_min(network_oracle_settings.os_updated_node_time):.1f} min",
                style="yellow",
            ),
        )
        config_table.add_row(
            "Min Aggregation Time:",
            Text(
                f"{self.posixtime_to_min(network_oracle_settings.os_aggregate_time):.1f} min",
                style="yellow",
            ),
        )
        config_table.add_row(
            "Price Change Threshold:",
            Text(f"{network_oracle_settings.os_aggregate_change/100:.1f}%", style="magenta"),
        )
        config_table.add_row(
            "Min Pool Recharge:",
            Text(f"{network_oracle_settings.os_minimum_deposit} tokens", style="green"),
        )
        config_table.add_row(
            "Aggregate Timeout:",
            Text(
                f"{self.posixtime_to_min(network_oracle_settings.os_aggregate_valid_range):.1f} min",
                style="yellow",
            ),
        )

        node, aggregate, platform = self.get_price_rewards(network_oracle_settings)
        config_table.add_row("")
        config_table.add_row("[bold]Rewards[/bold]", "")
        config_table.add_row("  Node Reward:", Text(f"{node} C3", style="bold green"))
        config_table.add_row(
            "  Aggregate Reward:", Text(f"{aggregate} C3", style="bold green")
        )
        config_table.add_row(
            "  Platform Reward:", Text(f"{platform} C3", style="bold green")
        )

        config_table.add_row("")
        config_table.add_row("[bold]Consensus Settings[/bold]", "")
        config_table.add_row(
            "  IQR Multiplier:",
            Text(str(network_oracle_settings.os_iqr_multiplier), style="cyan"),
        )
        config_table.add_row(
            "  Divergence Percentage:",
            Text(f"{network_oracle_settings.os_divergence/100:.1f}%", style="cyan"),
        )

        signatories, minimum_signatories = self.get_platform_signatories_info(
            network_oracle_settings
        )
        config_table.add_row("")
        config_table.add_row("[bold]Platform Signatories[/bold]", "")
        config_table.add_row(
            "  Total Signatories:", Text(str(len(signatories)), style="blue")
        )
        config_table.add_row(
            "  Minimum Required:", Text(str(minimum_signatories), style="blue")
        )

        console.print(Panel(config_table, border_style="green", padding=(1, 2)))
