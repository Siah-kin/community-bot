# Dune Queries for BONZI Metrics

Create these queries at https://dune.com/queries - click "New Query", paste SQL, save, run, note the query ID.

---

## BONZI QUERIES

### 1. BONZI Staker Retention
```sql
SELECT
    action,
    COUNT(DISTINCT wallet) as wallets
FROM (
    SELECT
        "from" as wallet,
        CASE WHEN bytearray_substring(data,1,4) = 0x666da64f THEN 'staking' ELSE 'exited' END as action,
        ROW_NUMBER() OVER (PARTITION BY "from" ORDER BY block_time DESC) as rn
    FROM ethereum.transactions
    WHERE "to" = 0x3618158bb8d07111e476f4de28676dff050d1a53
        AND success = true
        AND block_time > DATE '2024-12-01'
        AND bytearray_substring(data,1,4) IN (0x666da64f, 0x2e1a7d4d)
)
WHERE rn = 1
GROUP BY action
```

### 2. BONZI Diamond Hands
```sql
SELECT COUNT(DISTINCT "from") as diamond_hands
FROM ethereum.transactions t1
WHERE "to" = 0x3618158bb8d07111e476f4de28676dff050d1a53
    AND success = true
    AND block_time > DATE '2024-12-01'
    AND bytearray_substring(data,1,4) = 0x666da64f
    AND NOT EXISTS (
        SELECT 1 FROM ethereum.transactions t2
        WHERE t2."from" = t1."from"
            AND t2."to" = 0x3618158bb8d07111e476f4de28676dff050d1a53
            AND t2.block_time > DATE '2024-12-01'
            AND bytearray_substring(t2.data,1,4) = 0x2e1a7d4d
    )
```

### 3. BONZI Weekly Trend
```sql
SELECT
    DATE_TRUNC('week', block_time) as week,
    COUNT(*) FILTER (WHERE bytearray_substring(data,1,4) = 0x666da64f) as stakes,
    COUNT(*) FILTER (WHERE bytearray_substring(data,1,4) = 0x2e1a7d4d) as unstakes
FROM ethereum.transactions
WHERE "to" = 0x3618158bb8d07111e476f4de28676dff050d1a53
    AND success = true
    AND block_time > DATE '2024-12-01'
GROUP BY 1
ORDER BY 1 DESC
LIMIT 12
```

### 4. BONZI Tenure
```sql
SELECT
    ROUND(AVG(DATE_DIFF('day', first_stake, NOW()))) as avg_tenure_days,
    MAX(DATE_DIFF('day', first_stake, NOW())) as max_tenure_days
FROM (
    SELECT "from" as wallet, MIN(block_time) as first_stake
    FROM ethereum.transactions
    WHERE "to" = 0x3618158bb8d07111e476f4de28676dff050d1a53
        AND success = true
        AND bytearray_substring(data,1,4) = 0x666da64f
        AND block_time > DATE '2024-12-01'
    GROUP BY 1
)
```

---

## MURAD METRICS (Both Tokens)

### 5. VISTA HHI (Holder Concentration Index)
```sql
WITH holder_balances AS (
    SELECT
        "to" as holder,
        SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000 THEN value ELSE 0 END)
        - SUM(CASE WHEN "to" = 0x0000000000000000000000000000000000000000 THEN value ELSE 0 END)
        + SUM(CASE WHEN "to" = holder THEN value ELSE 0 END)
        - SUM(CASE WHEN "from" = holder THEN value ELSE 0 END) as balance
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address = 0xc9bca88b04581699fab5aa276ccaff7df957cbbf
    GROUP BY 1
    HAVING balance > 0
),
total AS (
    SELECT SUM(balance) as total_supply FROM holder_balances
),
shares AS (
    SELECT
        holder,
        balance,
        100.0 * balance / total.total_supply as pct_share
    FROM holder_balances, total
)
SELECT
    COUNT(*) as total_holders,
    ROUND(SUM(CASE WHEN rn <= 10 THEN pct_share ELSE 0 END), 2) as top_10_pct,
    ROUND(SUM(pct_share * pct_share), 0) as hhi_score
FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY balance DESC) as rn FROM shares
)
```

### 6. BONZI HHI (Holder Concentration Index)
```sql
WITH holder_balances AS (
    SELECT
        "to" as holder,
        SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000 THEN value ELSE 0 END)
        - SUM(CASE WHEN "to" = 0x0000000000000000000000000000000000000000 THEN value ELSE 0 END)
        + SUM(CASE WHEN "to" = holder THEN value ELSE 0 END)
        - SUM(CASE WHEN "from" = holder THEN value ELSE 0 END) as balance
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address = 0xd6175692026bcd7cb12a515e39cf0256ef35cb86
    GROUP BY 1
    HAVING balance > 0
),
total AS (
    SELECT SUM(balance) as total_supply FROM holder_balances
),
shares AS (
    SELECT
        holder,
        balance,
        100.0 * balance / total.total_supply as pct_share
    FROM holder_balances, total
)
SELECT
    COUNT(*) as total_holders,
    ROUND(SUM(CASE WHEN rn <= 10 THEN pct_share ELSE 0 END), 2) as top_10_pct,
    ROUND(SUM(pct_share * pct_share), 0) as hhi_score
FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY balance DESC) as rn FROM shares
)
```

### 7. VISTA $1K+ Holders
```sql
WITH holder_balances AS (
    SELECT
        "to" as holder,
        SUM(CASE WHEN "to" = holder THEN value ELSE 0 END)
        - SUM(CASE WHEN "from" = holder THEN value ELSE 0 END) as balance
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address = 0xc9bca88b04581699fab5aa276ccaff7df957cbbf
    GROUP BY 1
    HAVING balance > 0
),
with_usd AS (
    SELECT
        holder,
        balance,
        balance * 0.003 as usd_value -- approximate VISTA price
    FROM holder_balances
)
SELECT
    COUNT(*) FILTER (WHERE usd_value >= 1000) as holders_1k_plus,
    COUNT(*) FILTER (WHERE usd_value >= 10000) as holders_10k_plus,
    COUNT(*) as total_holders
FROM with_usd
```

### 8. BONZI $1K+ Holders
```sql
WITH holder_balances AS (
    SELECT
        "to" as holder,
        SUM(CASE WHEN "to" = holder THEN value ELSE 0 END)
        - SUM(CASE WHEN "from" = holder THEN value ELSE 0 END) as balance
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address = 0xd6175692026bcd7cb12a515e39cf0256ef35cb86
    GROUP BY 1
    HAVING balance > 0
),
with_usd AS (
    SELECT
        holder,
        balance / 1e18 as balance_tokens,
        (balance / 1e18) * 0.0001 as usd_value -- approximate BONZI price
    FROM holder_balances
)
SELECT
    COUNT(*) FILTER (WHERE usd_value >= 1000) as holders_1k_plus,
    COUNT(*) FILTER (WHERE usd_value >= 10000) as holders_10k_plus,
    COUNT(*) as total_holders
FROM with_usd
```

---

## After Creating Queries

Update `fetch_metrics.py` with the new query IDs:

```python
QUERIES = {
    # VISTA
    'vista_hhi': 'NEW_ID_HERE',
    'vista_staker_retention': '6591349',
    'vista_diamond_hands': '6591316',
    'vista_weekly_trend': '6591328',
    'vista_tenure': '6591332',
    'vista_1k_holders': 'NEW_ID_HERE',

    # BONZI
    'bonzi_hhi': 'NEW_ID_HERE',
    'bonzi_staker_retention': 'NEW_ID_HERE',
    'bonzi_diamond_hands': 'NEW_ID_HERE',
    'bonzi_weekly_trend': 'NEW_ID_HERE',
    'bonzi_tenure': 'NEW_ID_HERE',
    'bonzi_1k_holders': 'NEW_ID_HERE',
}
```

---

## Contract Reference

| Token | Type | Address |
|-------|------|---------|
| VISTA | Token | `0xc9bca88b04581699fab5aa276ccaff7df957cbbf` |
| VISTA | Hardstake | `0xee5a6f8a55b02689138c195031d09bafdc7d278f` |
| BONZI | Token | `0xd6175692026bcd7cb12a515e39cf0256ef35cb86` |
| BONZI | Hardstake | `0x3618158bb8d07111e476f4de28676dff050d1a53` |
| BONZI | LP Pair | `0x970cf9b7346fbaea0588f03356a104100eb675e2` |
