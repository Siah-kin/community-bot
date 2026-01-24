# Bonzi Brand Widget

**One-line token purchase widget for any website.**

## Quick Start

```html
<script
  src="https://bonzi.bot/widget/embed.js"
  data-token="0xYourTokenAddress"
  data-symbol="$TOKEN">
</script>
```

## What It Does

- Email/Google/Apple login (no wallet app needed)
- Card payment via Coinbase Pay
- Auto-swap to your token on Base chain
- Mobile responsive, dark/light mode

## Files

| File | Purpose |
|------|---------|
| `embed.js` | One-line embed script |
| `brand-widget.html` | Full widget UI |
| `brand-widget.css` | Styling |
| `qr.html` | QR code generator for IRL |

## Configuration

| Attribute | Description | Default |
|-----------|-------------|---------|
| `data-token` | ERC-20 contract address | Required |
| `data-symbol` | Token display symbol | `$TOKEN` |
| `data-mode` | `inline`, `modal`, or `floating` | `inline` |
| `data-theme` | `light` or `dark` | `light` |
| `data-testnet` | Use Base Sepolia | `false` |

## Display Modes

```html
<!-- Inline (renders in place) -->
<script src="embed.js" data-token="0x..." data-mode="inline"></script>

<!-- Modal (popup on button click) -->
<button onclick="BonziWidget.open()">Buy Token</button>
<script src="embed.js" data-token="0x..." data-mode="modal"></script>

<!-- Floating (sticky bottom-right button) -->
<script src="embed.js" data-token="0x..." data-mode="floating"></script>
```

## JavaScript API

```javascript
BonziWidget.open();           // Open modal
BonziWidget.close();          // Close modal
BonziWidget.isConnected();    // Check connection
BonziWidget.getAddress();     // Get wallet address

// Events
BonziWidget.on('connected', (addr) => console.log(addr));
BonziWidget.on('purchase', (data) => console.log(data.txHash));
```

## Full Documentation

**Complete integration guide with Bootstrap/Tailwind/React/Vue templates:**

[Brand Starter Kit](https://bonzi.bot/docs/brand-starter-kit)

Includes:
- Full-page templates (copy-paste ready)
- CSS variable customization
- React/Next.js component
- Vue.js component
- Testnet testing guide

## Technical Details

- **Chain:** Base (Coinbase L2)
- **Wallet:** Coinbase CDP embedded wallets
- **Swap:** 0x API / Uniswap
- **Gas:** ~$0.01 per transaction

## Support

- Telegram: @BonziBot
- Docs: bonzi.bot/docs
