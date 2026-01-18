"""
Web3 contract interactions for Etherfun token launches.

This module handles all blockchain interactions:
- Token deployment via SafeTokenFactory
- Router approval
- Liquidity launch via EtherVistaRouter
- Gas estimation
"""

import logging
from typing import Optional
from dataclasses import dataclass
from web3 import Web3
from web3.exceptions import ContractLogicError
from eth_account import Account

from .config import (
    CONTRACTS,
    GAS_LIMITS,
    SAFE_TOKEN_FACTORY_ABI,
    ERC20_ABI,
    ROUTER_ABI,
    FACTORY_ABI,
    DEFAULT_FEES,
)
from monitoring.observe import observe

logger = logging.getLogger(__name__)


@dataclass
class TransactionData:
    """Unsigned transaction data for web widget signing."""
    to: str
    data: str
    value: int
    gas: int
    chain_id: int = 1  # Mainnet

    def to_dict(self) -> dict:
        return {
            "to": self.to,
            "data": self.data,
            "value": hex(self.value),
            "gas": hex(self.gas),
            "chainId": hex(self.chain_id),
        }


@dataclass
class GasEstimate:
    """Gas cost breakdown for a token launch."""
    create_token_gas: int
    approve_gas: int
    launch_gas: int
    total_gas: int
    gas_price_wei: int
    total_cost_wei: int
    total_cost_eth: float

    def to_dict(self) -> dict:
        return {
            "create_token_gas": self.create_token_gas,
            "approve_gas": self.approve_gas,
            "launch_gas": self.launch_gas,
            "total_gas": self.total_gas,
            "gas_price_gwei": self.gas_price_wei / 1e9,
            "total_cost_eth": self.total_cost_eth,
        }


class EtherfunContracts:
    """
    Interface to Ethervista/Etherfun smart contracts.

    Generates unsigned transaction data for web widget signing.
    Does NOT hold or manage private keys.
    """

    def __init__(self, rpc_url: str = "https://eth.llamarpc.com"):
        """
        Initialize with an Ethereum RPC endpoint.

        Args:
            rpc_url: Ethereum JSON-RPC endpoint (default: public LlamaRPC)
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        # Initialize contracts
        self.token_factory = self.w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACTS["safe_token_factory"]),
            abi=SAFE_TOKEN_FACTORY_ABI,
        )
        self.router = self.w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACTS["router"]),
            abi=ROUTER_ABI,
        )
        self.factory = self.w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACTS["factory"]),
            abi=FACTORY_ABI,
        )

    def is_connected(self) -> bool:
        """Check if connected to Ethereum network."""
        try:
            return self.w3.is_connected()
        except Exception:
            return False

    def get_gas_price(self) -> int:
        """Get current gas price in wei."""
        return self.w3.eth.gas_price

    def get_balance(self, address: str) -> float:
        """Get ETH balance for an address."""
        balance_wei = self.w3.eth.get_balance(
            Web3.to_checksum_address(address)
        )
        return self.w3.from_wei(balance_wei, "ether")

    @observe("etherfun.estimate_launch_cost")
    def estimate_launch_cost(self) -> GasEstimate:
        """
        Estimate total gas cost for a token launch.

        Returns:
            GasEstimate with breakdown of costs
        """
        gas_price = self.get_gas_price()

        create_gas = GAS_LIMITS["create_token"]
        approve_gas = GAS_LIMITS["approve"]
        launch_gas = GAS_LIMITS["launch"]
        total_gas = create_gas + approve_gas + launch_gas

        total_cost_wei = total_gas * gas_price
        total_cost_eth = float(self.w3.from_wei(total_cost_wei, "ether"))

        return GasEstimate(
            create_token_gas=create_gas,
            approve_gas=approve_gas,
            launch_gas=launch_gas,
            total_gas=total_gas,
            gas_price_wei=gas_price,
            total_cost_wei=total_cost_wei,
            total_cost_eth=total_cost_eth,
        )

    @observe("etherfun.build_create_token_tx")
    def build_create_token_tx(
        self,
        name: str,
        symbol: str,
        supply: int,
        creator_address: str,
        vista_only: bool = True,
    ) -> TransactionData:
        """
        Build unsigned transaction for token creation.

        Args:
            name: Token name (e.g., "Pepe Token")
            symbol: Token symbol (e.g., "PEPE")
            supply: Total supply (will be multiplied by 10^18)
            creator_address: Address that will own the tokens
            vista_only: If True, token can only trade on Ethervista

        Returns:
            TransactionData for signing
        """
        # Convert supply to wei (18 decimals)
        supply_wei = supply * (10 ** 18)

        # Build transaction data
        tx_data = self.token_factory.functions.create(
            name,
            symbol,
            supply_wei,
            vista_only,
        ).build_transaction({
            "from": Web3.to_checksum_address(creator_address),
            "gas": GAS_LIMITS["create_token"],
            "nonce": self.w3.eth.get_transaction_count(
                Web3.to_checksum_address(creator_address)
            ),
        })

        return TransactionData(
            to=CONTRACTS["safe_token_factory"],
            data=tx_data["data"],
            value=0,
            gas=GAS_LIMITS["create_token"],
        )

    @observe("etherfun.build_approve_tx")
    def build_approve_tx(
        self,
        token_address: str,
        owner_address: str,
        amount: Optional[int] = None,
    ) -> TransactionData:
        """
        Build unsigned transaction for router approval.

        Args:
            token_address: Address of the deployed token
            owner_address: Token owner address
            amount: Amount to approve (default: max uint256)

        Returns:
            TransactionData for signing
        """
        token = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=ERC20_ABI,
        )

        # Max approval if not specified
        if amount is None:
            amount = 2**256 - 1

        tx_data = token.functions.approve(
            Web3.to_checksum_address(CONTRACTS["router"]),
            amount,
        ).build_transaction({
            "from": Web3.to_checksum_address(owner_address),
            "gas": GAS_LIMITS["approve"],
            "nonce": self.w3.eth.get_transaction_count(
                Web3.to_checksum_address(owner_address)
            ) + 1,  # +1 because create_token is nonce 0
        })

        return TransactionData(
            to=token_address,
            data=tx_data["data"],
            value=0,
            gas=GAS_LIMITS["approve"],
        )

    @observe("etherfun.build_launch_tx")
    def build_launch_tx(
        self,
        token_address: str,
        token_amount: int,
        eth_amount: float,
        creator_address: str,
        buy_lp_fee: int = DEFAULT_FEES["buy_lp_fee"],
        sell_lp_fee: int = DEFAULT_FEES["sell_lp_fee"],
        buy_protocol_fee: int = DEFAULT_FEES["buy_protocol_fee"],
        sell_protocol_fee: int = DEFAULT_FEES["sell_protocol_fee"],
    ) -> TransactionData:
        """
        Build unsigned transaction for liquidity launch.

        Args:
            token_address: Address of the deployed token
            token_amount: Amount of tokens for LP (in token units, not wei)
            eth_amount: ETH to add as liquidity
            creator_address: Address to receive protocol fees
            *_fee: Fee rates in basis points (5 = 0.05%)

        Returns:
            TransactionData for signing
        """
        # Convert to wei
        token_amount_wei = token_amount * (10 ** 18)
        eth_amount_wei = self.w3.to_wei(eth_amount, "ether")

        tx_data = self.router.functions.launch(
            Web3.to_checksum_address(token_address),
            token_amount_wei,
            buy_lp_fee,
            sell_lp_fee,
            buy_protocol_fee,
            sell_protocol_fee,
            Web3.to_checksum_address(creator_address),
        ).build_transaction({
            "from": Web3.to_checksum_address(creator_address),
            "value": eth_amount_wei,
            "gas": GAS_LIMITS["launch"],
            "nonce": self.w3.eth.get_transaction_count(
                Web3.to_checksum_address(creator_address)
            ) + 2,  # +2 because create and approve are 0,1
        })

        return TransactionData(
            to=CONTRACTS["router"],
            data=tx_data["data"],
            value=eth_amount_wei,
            gas=GAS_LIMITS["launch"],
        )

    @observe("etherfun.get_pair_address")
    def get_pair_address(self, token_address: str) -> Optional[str]:
        """
        Get the LP pair address for a token.

        Args:
            token_address: Token contract address

        Returns:
            Pair address or None if not found
        """
        try:
            pair = self.factory.functions.getPair(
                Web3.to_checksum_address(token_address),
                Web3.to_checksum_address(CONTRACTS["weth"]),
            ).call()

            if pair == "0x0000000000000000000000000000000000000000":
                return None
            return pair
        except Exception as e:
            logger.error(f"Error getting pair address: {e}")
            return None

    def is_token_whitelisted(self, token_address: str) -> bool:
        """Check if a token was created via SafeTokenFactory."""
        try:
            return self.token_factory.functions.whitelistedTokens(
                Web3.to_checksum_address(token_address)
            ).call()
        except Exception:
            return False

    def build_all_launch_txs(
        self,
        name: str,
        symbol: str,
        supply: int,
        eth_liquidity: float,
        creator_address: str,
        lp_percentage: int = 80,
    ) -> list[TransactionData]:
        """
        Build all three transactions needed for a token launch.

        Args:
            name: Token name
            symbol: Token symbol
            supply: Total token supply
            eth_liquidity: ETH to add as initial liquidity
            creator_address: Deployer/owner address
            lp_percentage: Percentage of supply to add to LP (default 80%)

        Returns:
            List of 3 TransactionData objects [create, approve, launch]
        """
        lp_amount = int(supply * lp_percentage / 100)

        return [
            self.build_create_token_tx(name, symbol, supply, creator_address),
            # Note: approve and launch txs need the token address
            # which is only known after create tx is mined.
            # These will be built after create tx succeeds.
        ]

    def get_links(self, token_address: str) -> dict:
        """
        Generate useful links for a launched token.

        Args:
            token_address: Deployed token address

        Returns:
            Dict with links to various platforms
        """
        pair_address = self.get_pair_address(token_address)

        links = {
            "etherscan_token": f"https://etherscan.io/token/{token_address}",
            "etherfun": f"https://etherfun.app/token/{token_address}",
        }

        if pair_address:
            links["etherscan_pair"] = f"https://etherscan.io/address/{pair_address}"
            links["dexscreener"] = f"https://dexscreener.com/ethereum/{pair_address}"
            links["dextools"] = f"https://www.dextools.io/app/en/ether/pair-explorer/{pair_address}"

        return links
