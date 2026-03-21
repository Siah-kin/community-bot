# HARDLOCK LP Staking: MEV Risk Guide

## Risk Summary

| Risk | Impact | Mitigation |
|------|--------|------------|
| Frontrunning | You get worse price on stake/unstake | Use Flashbots RPC |
| Sandwich attacks | ~0.5-3% loss on large transactions | Split large stakes |
| 14-day lock exposure | Cannot exit during market volatility | Stake only what you can lock |

**Bottom line:** Without protection, MEV bots can extract value from your staking transactions. This guide explains how and what to do about it.

---

## What is MEV?

**Maximal Extractable Value (MEV)** is profit that miners/validators and specialized bots can extract by reordering, inserting, or censoring transactions in a block.

When you submit a transaction to stake LP tokens:
1. Your transaction sits in the public mempool (waiting area)
2. MEV bots scan the mempool looking for profitable opportunities
3. They can see your transaction before it's confirmed
4. They can pay higher gas to have their transaction processed first

Think of it like someone seeing your order at a restaurant and cutting in line to buy up all the ingredients, then selling them back to you at a markup.

---

## How MEV Affects Staking

### Frontrunning
A bot sees your large stake transaction and buys tokens before you, driving up the price. You end up paying more.

```
Your tx: Stake 10 ETH worth of LP
Bot sees this in mempool
Bot buys LP tokens (price goes up)
Your tx executes at higher price
Bot sells at profit
```

### Sandwich Attacks
The bot places two transactions around yours:
1. **Front**: Buy before you (price up)
2. **Your tx**: Executes at worse price
3. **Back**: Sell after you (captures profit)

You lose ~0.5-3% depending on transaction size and liquidity.

### Backrunning
Less harmful but still extracts value. Bot places transaction immediately after yours to arbitrage any price impact.

---

## The 14-Day Lock Risk

HARDLOCK requires a **14-day minimum stake period**. This creates unique MEV considerations:

1. **Entry timing matters**: If you get sandwiched on entry, you're locked at a worse position for 14 days
2. **Exit timing matters**: Unstaking is also visible in mempool and can be frontrun
3. **No emergency exit**: During high volatility, you cannot immediately unstake to avoid losses
4. **Compound effect**: MEV loss + 14-day lock + potential market movement

**Example scenario:**
- You stake during high activity, lose 2% to MEV
- Token drops 20% during lock period
- You unstake after 14 days, lose another 1% to MEV
- Total impact: Staking rewards may not cover losses

---

## How Flashbots RPC Protects You

**Flashbots** is a private transaction relay that bypasses the public mempool.

### How it works:
1. Your transaction goes directly to block builders (not public mempool)
2. MEV bots cannot see your transaction before it's included
3. No frontrunning or sandwich attacks possible
4. Transaction either gets included privately or not at all

### Setup (MetaMask):
1. Go to Settings > Networks
2. Add new network:
   - **Network Name**: Flashbots Protect
   - **RPC URL**: `https://rpc.flashbots.net`
   - **Chain ID**: 1
   - **Currency**: ETH
3. Switch to this network for staking transactions

### Limitations:
- Slightly slower confirmation (waits for cooperative builders)
- Only works on Ethereum mainnet
- Some edge cases may still leak information

---

## Why Frontrunning Costs Real Money

Let's do the math on a $10,000 stake:

| Scenario | MEV Loss | Lock Period | Net Impact |
|----------|----------|-------------|------------|
| No protection, high gas period | ~$200-300 (2-3%) | 14 days | Significant |
| Flashbots, normal conditions | ~$0 | 14 days | Minimal |
| Large tx ($100k+), no protection | ~$1,000-3,000 | 14 days | Severe |

The larger your transaction, the more attractive it is to MEV bots. A $100k stake is a guaranteed target.

---

## Best Practices for LP Stakers

### Before Staking

1. **Use Flashbots RPC** - Non-negotiable for transactions over $1,000
2. **Check gas prices** - Avoid staking during network congestion (>50 gwei)
3. **Split large stakes** - Multiple smaller transactions are less attractive to bots
4. **Understand the lock** - Only stake what you can leave untouched for 14+ days

### Transaction Tips

- **Set reasonable slippage** - Too high (>1%) invites sandwich attacks
- **Avoid round numbers** - $10,000 exactly is more visible than $9,847
- **Time your transactions** - Low activity periods (weekends, early morning UTC) have less MEV competition

### After Staking

- **Plan your exit** - Same MEV risks apply to unstaking
- **Don't panic unstake** - Rushing during volatility often means worse execution
- **Use Flashbots for exit too** - Protect the full cycle

---

## Quick Reference

### Safe Staking Checklist

- [ ] Switched to Flashbots RPC
- [ ] Gas price is reasonable (<30 gwei ideal)
- [ ] Transaction size is under $50k (or split)
- [ ] Slippage set to 0.5% or less
- [ ] Understand 14-day lock commitment
- [ ] Have exit strategy planned

### Resources

- [Flashbots Protect](https://protect.flashbots.net/) - Official setup guide
- [MEV Blocker](https://mevblocker.io/) - Alternative protection service
- [Etherscan Gas Tracker](https://etherscan.io/gastracker) - Check current gas prices

---

## Summary

MEV is a real cost that affects every DeFi user. For HARDLOCK stakers, the 14-day lock period amplifies the importance of getting good execution on entry and exit.

**The solution is simple:** Use Flashbots RPC, avoid staking during high gas periods, and split large transactions.

Five minutes of setup can save you hundreds of dollars.

---

*Last updated: January 2026*
