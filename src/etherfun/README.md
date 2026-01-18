# EtherFun Token Launcher

Open-source token launch module for ethical, gas-only token deployment via [EtherFun.app](https://etherfun.app).

## Architecture

```
etherfun/
├── __init__.py      # Module exports
├── config.py        # Contract addresses, ABIs, chain config
├── contracts.py     # Web3 contract interactions
├── launcher.py      # Core launch logic (validation, deployment)
└── ui_launch.py     # Telegram UI wizard (4-step flow)
```

## How It Works

1. **Symbol** - User enters token symbol (validated: 2-10 chars, alphanumeric)
2. **Name** - User enters token name (validated: 2-50 chars)
3. **Supply** - User enters total supply (validated: 1 to 1 trillion)
4. **Liquidity** - User sets initial ETH liquidity (minimum 0.01 ETH)

Deploy requires only gas - no platform fees, no hidden costs.

## Security

- Contract addresses hardcoded (no user input for contracts)
- All user inputs validated and sanitized
- Wallet connection via WalletConnect
- Transactions signed client-side (private keys never touch server)

## License

MIT - Same as EtherFun protocol.
