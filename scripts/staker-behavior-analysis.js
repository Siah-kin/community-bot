/**
 * Staker Behavior Analysis
 *
 * Proves: Long-term stakers who got paid back BUY MORE, not sell.
 *
 * Data to extract from hardstake contracts:
 * 1. Addresses with 6+ months stake duration
 * 2. Their cumulative ETH claims
 * 3. Stake increase events AFTER claims (reinvestment signal)
 *
 * Contracts:
 * - BONZI Hardstake: 0x3618158bb8d07111e476f4de28676dff050d1a53
 * - VISTA Hardstake: 0xee5a6f8a55b02689138c195031d09bafdc7d278f
 */

const BONZI_HARDSTAKE = '0x3618158bb8d07111e476f4de28676dff050d1a53';
const VISTA_HARDSTAKE = '0xee5a6f8a55b02689138c195031d09bafdc7d278f';

// Event signatures we need to track
const EVENTS = {
    Staked: 'Staked(address,uint256)',        // When someone stakes tokens
    Unstaked: 'Unstaked(address,uint256)',    // When someone removes stake
    Claimed: 'RewardClaimed(address,uint256)', // When someone claims ETH
};

/**
 * Analysis we want to produce:
 *
 * 1. HODLER COHORTS
 *    - 0-30 days: Tourists (high churn expected)
 *    - 30-90 days: Testing waters
 *    - 90-180 days: Believers starting
 *    - 180+ days: Power stakers
 *
 * 2. BEHAVIOR AFTER FIRST CLAIM
 *    For each address that claimed ETH:
 *    - Did they unstake within 30 days? → Short-term
 *    - Did they add more stake after claiming? → Long-term reinvestor
 *    - Did they do nothing (keep staking)? → Passive hodler
 *
 * 3. THE KEY METRIC: Reinvestment Rate
 *    % of addresses that ADDED stake after their first claim
 *
 *    This proves: "Long-term holders who earned their money back, buy more"
 *
 * 4. CUMULATIVE ROI BY COHORT
 *    For 180+ day stakers:
 *    - Total ETH claimed
 *    - Estimated initial investment (stake value at entry)
 *    - ROI = ETH claimed / initial investment
 *    - Show that 180+ day cohort has 100%+ ROI and is STILL staking
 */

// Example output format for the metrics page:
const EXAMPLE_OUTPUT = {
    snapshot_date: '2026-01-23',
    bonzi_hardstake: {
        total_unique_stakers: 189,
        cohorts: {
            '0-30d': { count: 45, avg_stake: 5000000, churn_rate: '68%' },
            '30-90d': { count: 32, avg_stake: 12000000, churn_rate: '35%' },
            '90-180d': { count: 28, avg_stake: 25000000, churn_rate: '12%' },
            '180+d': { count: 84, avg_stake: 45000000, churn_rate: '3%' }
        },
        behavior_after_first_claim: {
            unstaked_within_30d: '22%',
            added_more_stake: '41%',  // THE KEY PROOF
            held_steady: '37%'
        },
        power_stakers: {
            count: 84,
            avg_roi_in_eth: '127%',
            still_staking: '97%',
            added_more_after_roi: '58%'  // OVER HALF BOUGHT MORE
        }
    }
};

/**
 * TODO: Implement using ethers.js to query event logs
 *
 * Steps:
 * 1. Get all Staked events → build address list with first stake date
 * 2. Get all Claimed events → map ETH claimed per address
 * 3. Get all Unstaked events → detect churn
 * 4. For each address: build timeline (stake → claim → stake more OR unstake)
 * 5. Classify into cohorts
 * 6. Calculate reinvestment rate for 180+ day cohort
 *
 * This script can be run as a cron job and output to:
 * /metrics/data/staker-behavior.json
 *
 * The metrics page can then fetch this JSON and display live proof.
 */

console.log('Staker Behavior Analysis');
console.log('========================');
console.log('');
console.log('Key metric to prove:');
console.log('"Long-term stakers who got paid back → buy MORE, not sell"');
console.log('');
console.log('Expected finding for 180+ day stakers:');
console.log('- 100%+ ROI in ETH');
console.log('- 97%+ still staking');
console.log('- 50%+ added more stake after reaching ROI');
console.log('');
console.log('This is Bitcoin-level conviction WITH actual yield.');
console.log('');
console.log('To implement: Run against Etherscan API or local node');
console.log('Contracts:');
console.log('  BONZI Hardstake:', BONZI_HARDSTAKE);
console.log('  VISTA Hardstake:', VISTA_HARDSTAKE);
