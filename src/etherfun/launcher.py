"""
Token launch orchestration for Etherfun.

Handles the full launch flow:
1. Validation
2. Session creation
3. Transaction building
4. Web widget URL generation
5. Status tracking
"""

import logging
import secrets
import time
import re
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from .config import LIMITS, RATE_LIMITS, CONTRACTS
from .contracts import EtherfunContracts, GasEstimate
from monitoring.observe import observe

logger = logging.getLogger(__name__)


class LaunchStatus(Enum):
    """Status of a token launch session."""
    PENDING = "pending"           # Waiting for user to sign
    CREATE_SIGNED = "create_signed"   # Token creation tx signed
    CREATE_CONFIRMED = "create_confirmed"  # Token deployed
    APPROVE_SIGNED = "approve_signed"     # Approval tx signed
    APPROVE_CONFIRMED = "approve_confirmed"  # Approval confirmed
    LAUNCH_SIGNED = "launch_signed"       # Launch tx signed
    COMPLETED = "completed"       # All done, token is live
    FAILED = "failed"             # Something went wrong
    EXPIRED = "expired"           # Session timed out


@dataclass
class LaunchParams:
    """Validated parameters for a token launch."""
    name: str
    symbol: str
    supply: int
    eth_liquidity: float
    lp_percentage: int = 80
    creator_address: Optional[str] = None

    def validate(self) -> list[str]:
        """Validate parameters, return list of errors."""
        errors = []

        # Symbol validation
        if not re.match(r'^[A-Za-z0-9]+$', self.symbol):
            errors.append("Symbol must be alphanumeric only")
        if len(self.symbol) < LIMITS["min_symbol_length"]:
            errors.append(f"Symbol too short (min {LIMITS['min_symbol_length']} chars)")
        if len(self.symbol) > LIMITS["max_symbol_length"]:
            errors.append(f"Symbol too long (max {LIMITS['max_symbol_length']} chars)")

        # Name validation
        if len(self.name) < LIMITS["min_name_length"]:
            errors.append(f"Name too short (min {LIMITS['min_name_length']} chars)")
        if len(self.name) > LIMITS["max_name_length"]:
            errors.append(f"Name too long (max {LIMITS['max_name_length']} chars)")

        # Supply validation
        if self.supply < LIMITS["min_supply"]:
            errors.append(f"Supply too low (min {LIMITS['min_supply']:,})")
        if self.supply > LIMITS["max_supply"]:
            errors.append(f"Supply too high (max {LIMITS['max_supply']:,})")

        # ETH validation
        if self.eth_liquidity < LIMITS["min_eth_liquidity"]:
            errors.append(f"ETH too low (min {LIMITS['min_eth_liquidity']} ETH)")
        if self.eth_liquidity > LIMITS["max_eth_liquidity"]:
            errors.append(f"ETH too high (max {LIMITS['max_eth_liquidity']} ETH)")

        # LP percentage
        if self.lp_percentage < 1 or self.lp_percentage > 100:
            errors.append("LP percentage must be 1-100")

        return errors


@dataclass
class LaunchSession:
    """
    A token launch session.

    Created when user initiates /launch, tracks state until completion.
    """
    session_id: str
    params: LaunchParams
    status: LaunchStatus = LaunchStatus.PENDING
    created_at: float = field(default_factory=time.time)

    # Telegram context
    user_id: Optional[int] = None
    chat_id: Optional[int] = None
    message_id: Optional[int] = None

    # Transaction hashes
    create_tx_hash: Optional[str] = None
    approve_tx_hash: Optional[str] = None
    launch_tx_hash: Optional[str] = None

    # Deployed addresses
    token_address: Optional[str] = None
    pair_address: Optional[str] = None

    # Error tracking
    error_message: Optional[str] = None

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        expiry_seconds = RATE_LIMITS["session_expiry_minutes"] * 60
        return time.time() - self.created_at > expiry_seconds

    @property
    def signing_url(self) -> str:
        """Generate the web widget URL for this session."""
        # TODO: Replace with actual hosted widget URL
        return f"https://bonzi.app/launch/{self.session_id}"

    def to_dict(self) -> dict:
        """Serialize session for storage/API."""
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "params": {
                "name": self.params.name,
                "symbol": self.params.symbol,
                "supply": self.params.supply,
                "eth_liquidity": self.params.eth_liquidity,
                "lp_percentage": self.params.lp_percentage,
            },
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "token_address": self.token_address,
            "pair_address": self.pair_address,
            "tx_hashes": {
                "create": self.create_tx_hash,
                "approve": self.approve_tx_hash,
                "launch": self.launch_tx_hash,
            },
            "error": self.error_message,
        }


@dataclass
class LaunchResult:
    """Result of a completed token launch."""
    success: bool
    token_address: Optional[str] = None
    pair_address: Optional[str] = None
    tx_hashes: dict = field(default_factory=dict)
    links: dict = field(default_factory=dict)
    error: Optional[str] = None
    gas_used: Optional[int] = None
    total_cost_eth: Optional[float] = None


class TokenLauncher:
    """
    Orchestrates token launches on Etherfun/Ethervista.

    Manages sessions, builds transactions, tracks status.
    Does NOT sign transactions - that happens in the web widget.
    """

    def __init__(self, rpc_url: str = "https://eth.llamarpc.com"):
        self.contracts = EtherfunContracts(rpc_url)
        self.sessions: dict[str, LaunchSession] = {}

    @observe("etherfun.create_session")
    def create_session(
        self,
        name: str,
        symbol: str,
        supply: int,
        eth_liquidity: float,
        user_id: Optional[int] = None,
        chat_id: Optional[int] = None,
        lp_percentage: int = 80,
    ) -> tuple[LaunchSession, list[str]]:
        """
        Create a new launch session.

        Args:
            name: Token name
            symbol: Token symbol
            supply: Total supply
            eth_liquidity: Initial ETH liquidity
            user_id: Telegram user ID
            chat_id: Telegram chat ID
            lp_percentage: % of supply for LP

        Returns:
            Tuple of (session, validation_errors)
        """
        # Build params
        params = LaunchParams(
            name=name,
            symbol=symbol.upper(),
            supply=supply,
            eth_liquidity=eth_liquidity,
            lp_percentage=lp_percentage,
        )

        # Validate
        errors = params.validate()
        if errors:
            return None, errors

        # Check rate limits (simplified - should use persistent storage)
        # TODO: Implement proper rate limiting with Redis/DB

        # Create session
        session_id = secrets.token_urlsafe(16)
        session = LaunchSession(
            session_id=session_id,
            params=params,
            user_id=user_id,
            chat_id=chat_id,
        )

        self.sessions[session_id] = session
        logger.info(f"Created launch session {session_id} for {symbol}")

        return session, []

    def get_session(self, session_id: str) -> Optional[LaunchSession]:
        """Get a session by ID."""
        session = self.sessions.get(session_id)
        if session and session.is_expired:
            session.status = LaunchStatus.EXPIRED
        return session

    def get_gas_estimate(self) -> GasEstimate:
        """Get current gas cost estimate."""
        return self.contracts.estimate_launch_cost()

    @observe("etherfun.build_create_tx")
    def build_create_tx(
        self,
        session_id: str,
        creator_address: str,
    ) -> dict:
        """
        Build the token creation transaction.

        Args:
            session_id: Session ID
            creator_address: User's wallet address

        Returns:
            Transaction data for signing
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        if session.status != LaunchStatus.PENDING:
            raise ValueError(f"Invalid session status: {session.status}")

        # Store creator address
        session.params.creator_address = creator_address

        # Build tx
        tx = self.contracts.build_create_token_tx(
            name=session.params.name,
            symbol=session.params.symbol,
            supply=session.params.supply,
            creator_address=creator_address,
            vista_only=True,
        )

        return tx.to_dict()

    @observe("etherfun.on_create_confirmed")
    def on_create_confirmed(
        self,
        session_id: str,
        tx_hash: str,
        token_address: str,
    ) -> dict:
        """
        Handle token creation confirmation.

        Args:
            session_id: Session ID
            tx_hash: Creation transaction hash
            token_address: Deployed token address

        Returns:
            Approve transaction data for signing
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")

        session.create_tx_hash = tx_hash
        session.token_address = token_address
        session.status = LaunchStatus.CREATE_CONFIRMED

        logger.info(f"Token created: {token_address} (session {session_id})")

        # Build approve tx
        tx = self.contracts.build_approve_tx(
            token_address=token_address,
            owner_address=session.params.creator_address,
        )

        return tx.to_dict()

    @observe("etherfun.on_approve_confirmed")
    def on_approve_confirmed(
        self,
        session_id: str,
        tx_hash: str,
    ) -> dict:
        """
        Handle approval confirmation.

        Args:
            session_id: Session ID
            tx_hash: Approval transaction hash

        Returns:
            Launch transaction data for signing
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")

        session.approve_tx_hash = tx_hash
        session.status = LaunchStatus.APPROVE_CONFIRMED

        logger.info(f"Approval confirmed (session {session_id})")

        # Calculate LP amount
        lp_amount = int(session.params.supply * session.params.lp_percentage / 100)

        # Build launch tx
        tx = self.contracts.build_launch_tx(
            token_address=session.token_address,
            token_amount=lp_amount,
            eth_amount=session.params.eth_liquidity,
            creator_address=session.params.creator_address,
        )

        return tx.to_dict()

    @observe("etherfun.on_launch_confirmed")
    def on_launch_confirmed(
        self,
        session_id: str,
        tx_hash: str,
    ) -> LaunchResult:
        """
        Handle launch confirmation.

        Args:
            session_id: Session ID
            tx_hash: Launch transaction hash

        Returns:
            LaunchResult with all details
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")

        session.launch_tx_hash = tx_hash
        session.status = LaunchStatus.COMPLETED

        # Get pair address
        session.pair_address = self.contracts.get_pair_address(session.token_address)

        # Get links
        links = self.contracts.get_links(session.token_address)

        logger.info(
            f"Launch complete! Token: {session.token_address}, "
            f"Pair: {session.pair_address} (session {session_id})"
        )

        return LaunchResult(
            success=True,
            token_address=session.token_address,
            pair_address=session.pair_address,
            tx_hashes={
                "create": session.create_tx_hash,
                "approve": session.approve_tx_hash,
                "launch": session.launch_tx_hash,
            },
            links=links,
        )

    @observe("etherfun.fail_session")
    def fail_session(self, session_id: str, error: str) -> None:
        """Mark a session as failed."""
        session = self.get_session(session_id)
        if session:
            session.status = LaunchStatus.FAILED
            session.error_message = error
            logger.error(f"Session {session_id} failed: {error}")

    def get_session_summary(self, session_id: str) -> str:
        """
        Get a human-readable summary of a session.

        Args:
            session_id: Session ID

        Returns:
            Formatted summary string
        """
        session = self.get_session(session_id)
        if not session:
            return "Session not found"

        gas = self.get_gas_estimate()

        summary = f"""
**Ready to launch {session.params.symbol}!**

**Token Details**
- Name: {session.params.name}
- Symbol: {session.params.symbol}
- Supply: {session.params.supply:,}
- LP: {session.params.lp_percentage}% of supply

**Liquidity**
- ETH: {session.params.eth_liquidity} ETH
- Estimated gas: ~${gas.total_cost_eth * 2500:.2f} (at current prices)

**Sign here:** {session.signing_url}
(expires in {RATE_LIMITS['session_expiry_minutes']} minutes)
"""
        return summary.strip()

    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count removed."""
        expired = [
            sid for sid, s in self.sessions.items()
            if s.is_expired
        ]
        for sid in expired:
            del self.sessions[sid]
        return len(expired)
