"""Read C3 Network configuration"""

from pycardano import Address, MultiAsset, BlockFrostChainContext
from .datums import GenericData, AggDatum, OracleSettings, OraclePlatform
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()


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

            oracle_feed_utxo = next(
                (
                    utxo
                    for utxo in oracle_utxos
                    if utxo.output.amount.multi_asset == self.network_feed_nft
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
                    if hasattr(datum, 'cbor') and datum.cbor:
                        oracle_inline_datum = GenericData.from_cbor(datum.cbor)

                        price = float(oracle_inline_datum.price_data.get_price()) / 1000000
                        creation_time = self.format_timestamp(
                            oracle_inline_datum.price_data.get_timestamp()
                        )
                        expiration_time = self.format_timestamp(
                            oracle_inline_datum.price_data.get_expiry()
                        )

                        table = Table(title="📊 CHARLI3 - Oracle Feed", show_header=False)
                        table.add_row("Last Price:", Text(f"${price:.6f}", style="bold cyan"))
                        table.add_row("Creation Time:", Text(creation_time, style="green"))
                        table.add_row("Expiration Time:", Text(expiration_time, style="yellow"))

                        panel = Panel(table, border_style="blue", padding=(1, 2))
                        console.print(panel)
            except Exception as datum_error:
                console.print(f"[red]Error parsing datum: {type(datum_error).__name__}: {str(datum_error)}[/red]")
                raise

        except ValueError as e:
            console.print(f"[red]Error retrieving oracle feed: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Error retrieving oracle feed: {type(e).__name__}: {e}[/red]")

    def get_all_network_configurations(self):
        """Fetch all Aggregate UTxO Configurations and sort by creation time (ascending)"""
        try:
            oracle_utxos = self.context.utxos(str(self.network_address))

            aggregate_utxos = []
            for utxo in oracle_utxos:
                if utxo.output.amount.multi_asset >= self.aggregate_state_nft:
                    try:
                        aggregate_state_inline_datum: AggDatum = AggDatum.from_cbor(
                            utxo.output.datum.cbor
                        )
                        # Store tuple of (creation_time, settings, utxo_object)
                        # Using transaction input index as a proxy for creation order
                        aggregate_utxos.append((
                            utxo.input.transaction_id,
                            aggregate_state_inline_datum.aggstate.ag_settings,
                            utxo
                        ))
                    except Exception as e:
                        console.print(f"[yellow]Warning: Failed to parse aggregate UTXO: {e}[/yellow]")

            if not aggregate_utxos:
                raise ValueError("No matching Aggregate State UTxOs found.")

            # Sort by transaction ID (as a proxy for creation order)
            aggregate_utxos.sort(key=lambda x: str(x[0]))
            return aggregate_utxos

        except ValueError as e:
            raise ValueError("Failed to fetch network configurations: " + str(e))
        except Exception as e:
            raise Exception(
                "An unexpected error occurred while fetching network configurations: "
                + str(e)
            )

    def get_network_configuration(self):
        """Fetch the most recent Aggregate UTxO Configuration Using the NFT Identifier"""
        try:
            aggregate_utxos = self.get_all_network_configurations()
            # Return the last (most recent) configuration
            return aggregate_utxos[-1][1]

        except (ValueError, IndexError) as e:
            raise ValueError("Failed to fetch network configuration: " + str(e))
        except Exception as e:
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

    def display_all_network_configurations(self):
        """Display all network configurations sorted by creation time"""
        aggregate_utxos = self.get_all_network_configurations()

        # Create table showing all aggregate UTxOs
        utxos_table = Table(title="📋 All Aggregate State UTxOs (Sorted by Creation Time)", show_header=True)
        utxos_table.add_column("Index", style="cyan")
        utxos_table.add_column("Transaction ID", style="magenta")
        utxos_table.add_column("Output Index", style="yellow")

        for idx, (tx_id, settings, utxo) in enumerate(aggregate_utxos):
            utxos_table.add_row(
                str(idx + 1),
                str(tx_id)[:16] + "...",
                str(utxo.input.index)
            )

        panel = Panel(utxos_table, border_style="cyan", padding=(1, 2))
        console.print(panel)

        # Display details for each configuration
        for idx, (tx_id, settings, utxo) in enumerate(aggregate_utxos):
            console.print(f"\n[bold blue]Configuration #{idx + 1}[/bold blue]")
            config_table = Table(show_header=False)
            config_table.add_row("Transaction:", Text(str(tx_id)[:32] + "...", style="cyan"))
            config_table.add_row("Output Index:", Text(str(utxo.input.index), style="yellow"))
            config_table.add_row("Authorized Nodes:", Text(str(len(settings.os_node_list)), style="green"))
            config_table.add_row("Aggregation Threshold:", Text(f"{settings.os_updated_nodes/100:.1f}%", style="magenta"))
            config_table.add_row("Max Node Update Time:", Text(f"{self.posixtime_to_min(settings.os_updated_node_time):.1f} min", style="yellow"))
            config_table.add_row("Min Aggregation Time:", Text(f"{self.posixtime_to_min(settings.os_aggregate_time):.1f} min", style="yellow"))

            panel = Panel(config_table, border_style="green", padding=(1, 2))
            console.print(panel)

    def display_network_configuration(self):
        """Display the most recent network configuration"""
        network_oracle_settings = self.get_network_configuration()

        # Create main configuration table
        config_table = Table(title="⚙️  C3 Network Configuration", show_header=False)
        config_table.add_row("Contract Address:", Text(str(self.network_address), style="cyan"))
        config_table.add_row("Authorized Nodes:", Text(str(len(network_oracle_settings.os_node_list)), style="green"))
        config_table.add_row("Aggregation Threshold:", Text(f"{network_oracle_settings.os_updated_nodes/100:.1f}%", style="magenta"))
        config_table.add_row("Max Node Update Time:", Text(f"{self.posixtime_to_min(network_oracle_settings.os_updated_node_time):.1f} min", style="yellow"))
        config_table.add_row("Min Aggregation Time:", Text(f"{self.posixtime_to_min(network_oracle_settings.os_aggregate_time):.1f} min", style="yellow"))
        config_table.add_row("Price Change Threshold:", Text(f"{network_oracle_settings.os_aggregate_change/100:.1f}%", style="magenta"))
        config_table.add_row("Min Pool Recharge:", Text(f"{network_oracle_settings.os_minimum_deposit} tokens", style="green"))
        config_table.add_row("Aggregate Timeout:", Text(f"{self.posixtime_to_min(network_oracle_settings.os_aggregate_valid_range):.1f} min", style="yellow"))

        # Rewards section
        node, aggregate, platform = self.get_price_rewards(network_oracle_settings)
        config_table.add_row("")
        config_table.add_row("[bold]Rewards[/bold]", "")
        config_table.add_row("  Node Reward:", Text(f"{node} C3", style="bold green"))
        config_table.add_row("  Aggregate Reward:", Text(f"{aggregate} C3", style="bold green"))
        config_table.add_row("  Platform Reward:", Text(f"{platform} C3", style="bold green"))

        # Consensus settings
        config_table.add_row("")
        config_table.add_row("[bold]Consensus Settings[/bold]", "")
        config_table.add_row("  IQR Multiplier:", Text(str(network_oracle_settings.os_iqr_multiplier), style="cyan"))
        config_table.add_row("  Divergence Percentage:", Text(f"{network_oracle_settings.os_divergence/100:.1f}%", style="cyan"))

        # Signatories section
        signatories, minimum_signatories = self.get_platform_signatories_info(
            network_oracle_settings
        )
        config_table.add_row("")
        config_table.add_row("[bold]Platform Signatories[/bold]", "")
        config_table.add_row("  Total Signatories:", Text(str(len(signatories)), style="blue"))
        config_table.add_row("  Minimum Required:", Text(str(minimum_signatories), style="blue"))

        panel = Panel(config_table, border_style="green", padding=(1, 2))
        console.print(panel)
