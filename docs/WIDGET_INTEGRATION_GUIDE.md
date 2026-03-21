# Bonzi Brand Widget - Integration Guide

Let your users buy tokens without wallets, seed phrases, or crypto knowledge.

---

## Quick Start

Add this single line to your website:

```html
<script
  src="https://siah-kin.github.io/community-bot/widget/embed.js"
  data-token="0xYourTokenAddress"
  data-symbol="$TOKEN">
</script>
```

That's it. A "Buy $TOKEN" button appears. Users can purchase with just an email.

---

## How It Works

1. **User clicks "Buy $TOKEN"** on your website
2. **Email/Google/Apple login** - Coinbase creates an invisible wallet
3. **Add funds** - Card payment via Coinbase Onramp
4. **Automatic swap** - USDC converts to your token
5. **Done** - User sees their balance. No seed phrase. No storage.

**User stores:** Nothing
**User knows:** Their email

---

## Integration Options

### Option 1: Inline Widget

Embed the full widget directly on your page:

```html
<div id="buy-widget"></div>
<script
  src="https://siah-kin.github.io/community-bot/widget/embed.js"
  data-token="0xYourTokenAddress"
  data-symbol="$TOKEN"
  data-container="buy-widget"
  data-position="inline">
</script>
```

### Option 2: Modal Button

Show a button that opens the widget in a modal:

```html
<script
  src="https://siah-kin.github.io/community-bot/widget/embed.js"
  data-token="0xYourTokenAddress"
  data-symbol="$TOKEN"
  data-position="modal"
  data-button-text="Buy $TOKEN Now">
</script>
```

### Option 3: Floating Button

Fixed button in the corner of the screen:

```html
<script
  src="https://siah-kin.github.io/community-bot/widget/embed.js"
  data-token="0xYourTokenAddress"
  data-symbol="$TOKEN"
  data-position="floating">
</script>
```

---

## Configuration

| Attribute | Description | Default |
|-----------|-------------|---------|
| `data-token` | Your token contract address on Base | Required |
| `data-symbol` | Display symbol (e.g., $BONZI) | "$TOKEN" |
| `data-position` | "inline", "modal", or "floating" | "inline" |
| `data-container` | Target element ID for inline mode | auto |
| `data-width` | Widget width | "400px" |
| `data-height` | Widget height | "600px" |
| `data-button-text` | Custom button text | "Buy $TOKEN" |
| `data-button-color` | Button background color | "#7B2D8E" |
| `data-theme` | "light" or "dark" | "light" |
| `data-testnet` | Use Base Sepolia testnet | "false" |

---

## JavaScript API

Control the widget programmatically:

```javascript
// Open modal
BonziWidget.open();

// Close modal
BonziWidget.close();

// Update configuration
BonziWidget.configure({
  token: '0xNewTokenAddress',
  symbol: '$NEWTOKEN'
});
```

---

## Direct Embed (No Script)

Embed via iframe directly:

```html
<iframe
  src="https://siah-kin.github.io/community-bot/widget/brand-widget.html?token=0xYourToken&symbol=$TOKEN"
  width="400"
  height="600"
  frameborder="0"
  allow="payment *">
</iframe>
```

URL Parameters:
- `token` - Token contract address
- `symbol` - Display symbol
- `testnet` - Set to "true" for testnet
- `theme` - "light" or "dark"

---

## QR Codes for Stickers

Generate QR codes for IRL marketing:

1. Visit https://siah-kin.github.io/community-bot/widget/qr.html
2. Enter your token details
3. Download QR code or sticker design
4. Print and distribute

QR codes link directly to the widget with your token pre-filled.

---

## Supported Networks

| Network | Chain ID | Status |
|---------|----------|--------|
| Base Mainnet | 8453 | Production |
| Base Sepolia | 84532 | Testing |

---

## User Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. LOGIN                                               │
│     Email / Google / Apple / Existing Wallet            │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  2. FUND                                                │
│     Coinbase Onramp: Card → USDC on Base                │
│     Handles KYC, fraud protection, compliance           │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  3. SWAP                                                │
│     USDC → Your Token                                   │
│     DEX aggregator finds best rate                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  4. DONE                                                │
│     User sees token balance                             │
│     Wallet tied to their email                          │
└─────────────────────────────────────────────────────────┘
```

---

## Testing

### Testnet Mode

For development, use Base Sepolia:

```html
<script
  src="https://siah-kin.github.io/community-bot/widget/embed.js"
  data-token="0xTestnetTokenAddress"
  data-symbol="$TEST"
  data-testnet="true">
</script>
```

### Get Test Funds

1. Get Sepolia ETH from [Base Faucet](https://www.coinbase.com/faucets/base-ethereum-goerli-faucet)
2. Use the widget with testnet mode enabled
3. Test the full flow without real money

---

## Security

- **Coinbase CDP** - Enterprise security, SOC 2 compliant
- **Non-custodial** - User controls wallet via email recovery
- **No sensitive data** - Widget never sees private keys
- **HTTPS only** - All communication encrypted

---

## Pricing

**Coinbase CDP:** Free until September 2025, then pay-as-you-go

**On-ramp fees:** Standard Coinbase rates (varies by payment method)

**Swap fees:** DEX fees + Base gas (~$0.01)

---

## Support

- **GitHub Issues:** https://github.com/Siah-kin/community-bot/issues
- **Telegram:** https://t.me/ethervistatoken

---

## Changelog

### v1.0.0 (January 2026)
- Initial release
- Coinbase CDP integration
- Base mainnet + Sepolia support
- Email/Google/Apple login
- QR code generator

---

## License

MIT License - Use freely in commercial projects.

---

## Examples

### Minimal Integration

```html
<!DOCTYPE html>
<html>
<head>
  <title>Buy Our Token</title>
</head>
<body>
  <h1>Welcome to Our Project</h1>

  <!-- Widget appears here -->
  <script
    src="https://siah-kin.github.io/community-bot/widget/embed.js"
    data-token="0x1234..."
    data-symbol="$EXAMPLE">
  </script>
</body>
</html>
```

### Custom Styled Button

```html
<button onclick="BonziWidget.open()" style="
  background: linear-gradient(135deg, #7B2D8E, #5a1f69);
  color: white;
  padding: 16px 32px;
  border: none;
  border-radius: 12px;
  font-size: 18px;
  cursor: pointer;
">
  Get $EXAMPLE Now
</button>

<script
  src="https://siah-kin.github.io/community-bot/widget/embed.js"
  data-token="0x1234..."
  data-symbol="$EXAMPLE"
  data-position="modal">
</script>
```

### React Integration

```jsx
import { useEffect } from 'react';

function BuyWidget({ token, symbol }) {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://siah-kin.github.io/community-bot/widget/embed.js';
    script.dataset.token = token;
    script.dataset.symbol = symbol;
    script.dataset.position = 'modal';
    document.body.appendChild(script);

    return () => document.body.removeChild(script);
  }, [token, symbol]);

  return (
    <button onClick={() => window.BonziWidget?.open()}>
      Buy {symbol}
    </button>
  );
}
```

### Vue Integration

```vue
<template>
  <button @click="openWidget">Buy {{ symbol }}</button>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';

const props = defineProps(['token', 'symbol']);
let script;

onMounted(() => {
  script = document.createElement('script');
  script.src = 'https://siah-kin.github.io/community-bot/widget/embed.js';
  script.dataset.token = props.token;
  script.dataset.symbol = props.symbol;
  script.dataset.position = 'modal';
  document.body.appendChild(script);
});

onUnmounted(() => {
  if (script) document.body.removeChild(script);
});

const openWidget = () => window.BonziWidget?.open();
</script>
```

---

## Try It Now

Generate your embed code instantly: https://siah-kin.github.io/community-bot/#demo
