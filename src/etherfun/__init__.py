"""
Etherfun Token Launch Bridge

Enables communities to deploy tokens on Ethervista DEX directly from Telegram.
Uses permissionless contracts - user signs via web widget, Bonzi never touches keys.
"""

from .config import CONTRACTS, GAS_LIMITS

# Graceful import - web3 may not be installed
try:
    from .contracts import EtherfunContracts
    from .launcher import TokenLauncher, LaunchResult
    WEB3_AVAILABLE = True
except ImportError:
    EtherfunContracts = None
    TokenLauncher = None
    LaunchResult = None
    WEB3_AVAILABLE = False

__all__ = [
    "CONTRACTS",
    "GAS_LIMITS",
    "EtherfunContracts",
    "TokenLauncher",
    "LaunchResult",
    "WEB3_AVAILABLE",
]
