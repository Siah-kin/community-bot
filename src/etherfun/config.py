"""
Etherfun contract addresses and configuration.

All contracts are on Ethereum Mainnet.
Source: https://github.com/Ethervista/Deployed-Contracts
"""

# Contract Addresses (Mainnet)
CONTRACTS = {
    "safe_token_factory": "0x1a97A037A120Db530dDCe8370e24EaD0FE9cf5d0",
    "router": "0xCEDd366065A146a039B92Db35756ecD7688FCC77",
    "factory": "0x9a27cb5ae0B2cEe0bb71f9A85C0D60f3920757B4",
    "weth": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "vista_token": "0xC9bCa88B04581699fAb5aa276CCafF7Df957cbbf",
}

# Gas Limits (conservative estimates)
GAS_LIMITS = {
    "create_token": 900_000,
    "approve": 60_000,
    "launch": 400_000,
    "total_estimate": 1_360_000,
}

# Validation Limits
LIMITS = {
    "min_supply": 1_000_000,
    "max_supply": 1_000_000_000_000_000,
    "min_eth_liquidity": 0.01,
    "max_eth_liquidity": 100.0,
    "min_symbol_length": 2,
    "max_symbol_length": 8,
    "min_name_length": 2,
    "max_name_length": 64,
}

# Rate Limits
RATE_LIMITS = {
    "max_launches_per_user_per_day": 3,
    "max_launches_per_community_per_day": 10,
    "min_account_age_days": 0,  # Set to 7 in production
    "session_expiry_minutes": 15,
}

# Default Fee Configuration (basis points, 100 = 1%)
DEFAULT_FEES = {
    "buy_lp_fee": 5,        # 0.05% to LPs on buys
    "sell_lp_fee": 5,       # 0.05% to LPs on sells
    "buy_protocol_fee": 0,  # 0% to creator on buys
    "sell_protocol_fee": 0, # 0% to creator on sells
}

# ABIs (minimal - only functions we need)
SAFE_TOKEN_FACTORY_ABI = [
    {
        "name": "create",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "name", "type": "string"},
            {"name": "symbol", "type": "string"},
            {"name": "supply", "type": "uint256"},
            {"name": "vistaOnly", "type": "bool"},
        ],
        "outputs": [{"name": "", "type": "address"}],
    },
    {
        "name": "whitelistedTokens",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "", "type": "address"}],
        "outputs": [{"name": "", "type": "bool"}],
    },
    {
        "name": "safeTokenCreated",
        "type": "event",
        "inputs": [
            {"name": "token", "type": "address", "indexed": True},
            {"name": "creator", "type": "address", "indexed": True},
        ],
    },
]

ERC20_ABI = [
    {
        "name": "approve",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
    },
    {
        "name": "balanceOf",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "totalSupply",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}],
    },
]

ROUTER_ABI = [
    {
        "name": "launch",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {"name": "token", "type": "address"},
            {"name": "amountToken", "type": "uint256"},
            {"name": "buyLpFee", "type": "uint8"},
            {"name": "sellLpFee", "type": "uint8"},
            {"name": "buyProtocolFee", "type": "uint8"},
            {"name": "sellProtocolFee", "type": "uint8"},
            {"name": "protocolAddress", "type": "address"},
        ],
        "outputs": [
            {"name": "amountTokenActual", "type": "uint256"},
            {"name": "amountETH", "type": "uint256"},
            {"name": "liquidity", "type": "uint256"},
        ],
    },
    {
        "name": "addLiquidityETH",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {"name": "token", "type": "address"},
            {"name": "amountTokenDesired", "type": "uint256"},
            {"name": "amountTokenMin", "type": "uint256"},
            {"name": "amountETHMin", "type": "uint256"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "outputs": [
            {"name": "amountToken", "type": "uint256"},
            {"name": "amountETH", "type": "uint256"},
            {"name": "liquidity", "type": "uint256"},
        ],
    },
]

FACTORY_ABI = [
    {
        "name": "getPair",
        "type": "function",
        "stateMutability": "view",
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
        ],
        "outputs": [{"name": "pair", "type": "address"}],
    },
]
