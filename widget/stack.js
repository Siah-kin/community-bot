/**
 * Bonzi Stack Widget - Buy + Stake + Earn
 *
 * DOCUMENTATION: https://github.com/Siah-kin/community-bot/blob/main/widget/README.md
 *
 * A unified widget for the complete BONZI journey:
 * 1. Buy BONZI tokens
 * 2. Stake via Ethervista hardstake()
 * 3. Track and claim Euler rewards (ETH)
 *
 * Quick Start:
 * <script src="https://bonzi.bot/widget/stack.js"></script>
 *
 * With configuration:
 * <script src="https://bonzi.bot/widget/stack.js"
 *   data-token="0xd6175692026bcd7cb12a515e39cf0256ef35cb86"
 *   data-staking-contract="0xEE5a6F8a55B02689138c195031d09BAFDc7d278F"
 *   data-theme="light"
 * ></script>
 *
 * Options:
 *   data-token: Token contract address (default: BONZI)
 *   data-staking-contract: Hardstake contract address
 *   data-router: Ethervista Router address
 *   data-theme: "light" or "dark"
 *   data-container: Target container ID
 *   data-mode: "inline", "modal", or "floating"
 */
(function() {
    'use strict';

    // Contract addresses (Ethereum Mainnet)
    const CONTRACTS = {
        BONZI: '0xd6175692026bcd7cb12a515e39cf0256ef35cb86',
        ROUTER: '0xCEDd366065A146a039B92Db35756ecD7688FCC77',
        HARDSTAKE: '0xEE5a6F8a55B02689138c195031d09BAFDc7d278F'
    };

    // ABIs (minimal for our needs)
    const ABIS = {
        ERC20: [
            'function balanceOf(address) view returns (uint256)',
            'function approve(address spender, uint256 amount) returns (bool)',
            'function allowance(address owner, address spender) view returns (uint256)',
            'function decimals() view returns (uint8)',
            'function symbol() view returns (string)'
        ],
        ROUTER: [
            'function hardstake(address token, uint256 amount) external',
            'function unstake(address token, uint256 amount) external'
        ],
        HARDSTAKE: [
            'function stakes(address user, address token) view returns (uint256 amount, uint256 rewardDebt)',
            'function pendingRewards(address user, address token) view returns (uint256)',
            'function claim(address token) external',
            'function totalStaked(address token) view returns (uint256)'
        ]
    };

    // Get current script for data attributes
    const currentScript = document.currentScript || (function() {
        const scripts = document.getElementsByTagName('script');
        return scripts[scripts.length - 1];
    })();

    // Configuration
    const CONFIG = {
        token: currentScript.dataset.token || CONTRACTS.BONZI,
        stakingContract: currentScript.dataset.stakingContract || CONTRACTS.HARDSTAKE,
        router: currentScript.dataset.router || CONTRACTS.ROUTER,
        theme: currentScript.dataset.theme || 'light',
        container: currentScript.dataset.container || null,
        mode: currentScript.dataset.mode || 'inline',
        symbol: currentScript.dataset.symbol || '$BONZI',
        rpcUrl: 'https://eth.llamarpc.com',
        chainId: 1,
        buyWidgetUrl: currentScript.dataset.buyUrl || 'https://bonzi.bot/widget/brand-widget.html'
    };

    // State
    let provider = null;
    let signer = null;
    let address = null;
    let currentTab = 'buy';

    // Widget HTML template
    const WIDGET_HTML = `
        <div class="bonzi-stack-widget" data-theme="${CONFIG.theme}">
            <div class="stack-header">
                <div class="stack-logo">
                    <span class="logo-icon">B</span>
                    <span class="logo-text">Bonzi Stack</span>
                </div>
                <button class="stack-connect-btn" id="stack-connect">
                    Connect Wallet
                </button>
            </div>

            <div class="stack-tabs">
                <button class="stack-tab active" data-tab="buy">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="9" cy="21" r="1"/>
                        <circle cx="20" cy="21" r="1"/>
                        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
                    </svg>
                    Buy
                </button>
                <button class="stack-tab" data-tab="stake">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                        <path d="M2 17l10 5 10-5"/>
                        <path d="M2 12l10 5 10-5"/>
                    </svg>
                    Stake
                </button>
                <button class="stack-tab" data-tab="earn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="1" x2="12" y2="23"/>
                        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                    </svg>
                    Earn
                </button>
            </div>

            <div class="stack-content">
                <!-- Buy Tab -->
                <div class="stack-panel active" id="panel-buy">
                    <div class="panel-header">
                        <h3>Buy ${CONFIG.symbol}</h3>
                        <p>Purchase tokens with card or crypto</p>
                    </div>
                    <div class="buy-iframe-container">
                        <iframe
                            id="buy-widget-iframe"
                            src="${CONFIG.buyWidgetUrl}?token=${CONFIG.token}&symbol=${encodeURIComponent(CONFIG.symbol)}&embed=true"
                            allow="payment *; clipboard-write *"
                            loading="lazy"
                        ></iframe>
                    </div>
                </div>

                <!-- Stake Tab -->
                <div class="stack-panel" id="panel-stake">
                    <div class="panel-header">
                        <h3>Stake ${CONFIG.symbol}</h3>
                        <p>Lock tokens to earn ETH rewards</p>
                    </div>

                    <div class="stake-stats">
                        <div class="stat-card">
                            <span class="stat-label">Your Balance</span>
                            <span class="stat-value" id="stake-balance">--</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-label">Currently Staked</span>
                            <span class="stat-value" id="stake-staked">--</span>
                        </div>
                    </div>

                    <div class="stake-input-group">
                        <label>Amount to Stake</label>
                        <div class="input-with-max">
                            <input type="number" id="stake-amount" placeholder="0.0" min="0" step="any">
                            <button class="max-btn" id="stake-max">MAX</button>
                        </div>
                    </div>

                    <div class="stake-actions">
                        <button class="stack-btn primary" id="btn-stake" disabled>
                            Stake ${CONFIG.symbol}
                        </button>
                        <button class="stack-btn secondary" id="btn-unstake" disabled>
                            Unstake
                        </button>
                    </div>

                    <div class="stake-info">
                        <div class="info-row">
                            <span>Staking Contract</span>
                            <a href="https://etherscan.io/address/${CONFIG.stakingContract}" target="_blank" rel="noopener">
                                ${CONFIG.stakingContract.slice(0, 6)}...${CONFIG.stakingContract.slice(-4)}
                            </a>
                        </div>
                        <div class="info-row">
                            <span>Total Pool Staked</span>
                            <span id="total-staked">--</span>
                        </div>
                    </div>
                </div>

                <!-- Earn Tab -->
                <div class="stack-panel" id="panel-earn">
                    <div class="panel-header">
                        <h3>Euler Rewards</h3>
                        <p>Claim your ETH earnings</p>
                    </div>

                    <div class="rewards-card">
                        <div class="rewards-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                            </svg>
                        </div>
                        <div class="rewards-amount">
                            <span class="rewards-value" id="rewards-pending">0.000</span>
                            <span class="rewards-unit">ETH</span>
                        </div>
                        <span class="rewards-label">Claimable Rewards</span>
                    </div>

                    <button class="stack-btn primary large" id="btn-claim" disabled>
                        Claim Rewards
                    </button>

                    <div class="euler-explanation">
                        <h4>How Euler Rewards Work</h4>
                        <ul>
                            <li>Every swap on Ethervista generates fees</li>
                            <li>Fees are distributed to stakers in ETH</li>
                            <li>The longer you stake, the more you earn</li>
                            <li>Rewards accumulate in real-time</li>
                        </ul>
                    </div>

                    <div class="rewards-history" id="rewards-history">
                        <h4>Recent Claims</h4>
                        <p class="empty-state">Connect wallet to view history</p>
                    </div>
                </div>
            </div>

            <div class="stack-footer">
                <span>Powered by Ethervista</span>
                <a href="https://ethervista.app" target="_blank" rel="noopener">Learn more</a>
            </div>

            <!-- Loading Overlay -->
            <div class="stack-loading" id="stack-loading">
                <div class="loading-spinner"></div>
                <p id="loading-message">Processing...</p>
            </div>
        </div>
    `;

    // Widget CSS
    const WIDGET_CSS = `
        .bonzi-stack-widget {
            --stack-purple: #7C3AED;
            --stack-purple-dark: #5B21B6;
            --stack-purple-light: #A78BFA;
            --stack-green: #10B981;
            --stack-black: #1a1a1a;
            --stack-white: #ffffff;
            --stack-gray-50: #fafafa;
            --stack-gray-100: #f5f5f5;
            --stack-gray-200: #e5e5e5;
            --stack-gray-300: #d4d4d4;
            --stack-gray-500: #737373;
            --stack-gray-700: #404040;

            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            width: 100%;
            max-width: 420px;
            min-height: 600px;
            background: var(--stack-white);
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .bonzi-stack-widget[data-theme="dark"] {
            --stack-black: #ffffff;
            --stack-white: #1a1a1a;
            --stack-gray-50: #262626;
            --stack-gray-100: #333333;
            --stack-gray-200: #404040;
            --stack-gray-300: #525252;
            --stack-gray-500: #a3a3a3;
            --stack-gray-700: #d4d4d4;
        }

        /* Header */
        .stack-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            border-bottom: 1px solid var(--stack-gray-200);
        }

        .stack-logo {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .stack-logo .logo-icon {
            width: 32px;
            height: 32px;
            background: var(--stack-purple);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
        }

        .stack-logo .logo-text {
            font-size: 18px;
            font-weight: 700;
            color: var(--stack-purple);
        }

        .stack-connect-btn {
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
            background: var(--stack-purple);
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .stack-connect-btn:hover {
            background: var(--stack-purple-dark);
        }

        .stack-connect-btn.connected {
            background: var(--stack-gray-100);
            color: var(--stack-black);
        }

        /* Tabs */
        .stack-tabs {
            display: flex;
            border-bottom: 1px solid var(--stack-gray-200);
        }

        .stack-tab {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 14px 8px;
            font-size: 14px;
            font-weight: 600;
            color: var(--stack-gray-500);
            background: none;
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
        }

        .stack-tab:hover {
            color: var(--stack-purple);
        }

        .stack-tab.active {
            color: var(--stack-purple);
            border-bottom-color: var(--stack-purple);
        }

        .stack-tab svg {
            width: 18px;
            height: 18px;
        }

        /* Content */
        .stack-content {
            flex: 1;
            overflow-y: auto;
        }

        .stack-panel {
            display: none;
            padding: 20px;
            flex-direction: column;
            gap: 20px;
        }

        .stack-panel.active {
            display: flex;
        }

        .panel-header {
            text-align: center;
        }

        .panel-header h3 {
            font-size: 20px;
            font-weight: 700;
            color: var(--stack-black);
            margin-bottom: 4px;
        }

        .panel-header p {
            font-size: 14px;
            color: var(--stack-gray-500);
        }

        /* Buy Tab */
        .buy-iframe-container {
            flex: 1;
            min-height: 400px;
            border-radius: 12px;
            overflow: hidden;
            background: var(--stack-gray-50);
        }

        .buy-iframe-container iframe {
            width: 100%;
            height: 100%;
            min-height: 400px;
            border: none;
        }

        /* Stake Tab */
        .stake-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .stat-card {
            background: var(--stack-gray-50);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }

        .stat-label {
            display: block;
            font-size: 12px;
            color: var(--stack-gray-500);
            margin-bottom: 4px;
        }

        .stat-value {
            font-size: 20px;
            font-weight: 700;
            color: var(--stack-black);
        }

        .stake-input-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .stake-input-group label {
            font-size: 14px;
            font-weight: 600;
            color: var(--stack-gray-700);
        }

        .input-with-max {
            display: flex;
            border: 2px solid var(--stack-gray-200);
            border-radius: 12px;
            overflow: hidden;
        }

        .input-with-max:focus-within {
            border-color: var(--stack-purple);
        }

        .input-with-max input {
            flex: 1;
            padding: 14px 16px;
            font-size: 18px;
            font-weight: 600;
            border: none;
            outline: none;
            background: transparent;
            color: var(--stack-black);
        }

        .max-btn {
            padding: 14px 16px;
            font-size: 14px;
            font-weight: 700;
            color: var(--stack-purple);
            background: var(--stack-gray-50);
            border: none;
            cursor: pointer;
            transition: background 0.2s;
        }

        .max-btn:hover {
            background: var(--stack-gray-100);
        }

        .stake-actions {
            display: flex;
            gap: 12px;
        }

        .stake-info {
            background: var(--stack-gray-50);
            border-radius: 12px;
            padding: 16px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            font-size: 13px;
        }

        .info-row:not(:last-child) {
            border-bottom: 1px solid var(--stack-gray-200);
        }

        .info-row span:first-child {
            color: var(--stack-gray-500);
        }

        .info-row a {
            color: var(--stack-purple);
            text-decoration: none;
        }

        .info-row a:hover {
            text-decoration: underline;
        }

        /* Earn Tab */
        .rewards-card {
            background: linear-gradient(135deg, var(--stack-purple) 0%, var(--stack-purple-dark) 100%);
            border-radius: 16px;
            padding: 32px;
            text-align: center;
            color: white;
        }

        .rewards-icon {
            width: 48px;
            height: 48px;
            margin: 0 auto 16px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .rewards-icon svg {
            width: 24px;
            height: 24px;
        }

        .rewards-amount {
            display: flex;
            align-items: baseline;
            justify-content: center;
            gap: 8px;
            margin-bottom: 8px;
        }

        .rewards-value {
            font-size: 36px;
            font-weight: 700;
        }

        .rewards-unit {
            font-size: 18px;
            font-weight: 600;
            opacity: 0.8;
        }

        .rewards-label {
            font-size: 14px;
            opacity: 0.9;
        }

        .euler-explanation {
            background: var(--stack-gray-50);
            border-radius: 12px;
            padding: 16px;
        }

        .euler-explanation h4 {
            font-size: 14px;
            font-weight: 700;
            color: var(--stack-black);
            margin-bottom: 12px;
        }

        .euler-explanation ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .euler-explanation li {
            position: relative;
            padding-left: 20px;
            font-size: 13px;
            color: var(--stack-gray-700);
            margin-bottom: 8px;
        }

        .euler-explanation li::before {
            content: '';
            position: absolute;
            left: 0;
            top: 6px;
            width: 8px;
            height: 8px;
            background: var(--stack-green);
            border-radius: 50%;
        }

        .rewards-history {
            background: var(--stack-gray-50);
            border-radius: 12px;
            padding: 16px;
        }

        .rewards-history h4 {
            font-size: 14px;
            font-weight: 700;
            color: var(--stack-black);
            margin-bottom: 12px;
        }

        .empty-state {
            font-size: 13px;
            color: var(--stack-gray-500);
            text-align: center;
            padding: 16px 0;
        }

        /* Buttons */
        .stack-btn {
            flex: 1;
            padding: 14px 20px;
            font-size: 15px;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .stack-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .stack-btn.primary {
            background: var(--stack-purple);
            color: white;
        }

        .stack-btn.primary:hover:not(:disabled) {
            background: var(--stack-purple-dark);
        }

        .stack-btn.secondary {
            background: var(--stack-gray-100);
            color: var(--stack-black);
        }

        .stack-btn.secondary:hover:not(:disabled) {
            background: var(--stack-gray-200);
        }

        .stack-btn.large {
            padding: 18px 24px;
            font-size: 16px;
        }

        /* Footer */
        .stack-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            border-top: 1px solid var(--stack-gray-200);
            font-size: 12px;
            color: var(--stack-gray-500);
        }

        .stack-footer a {
            color: var(--stack-purple);
            text-decoration: none;
        }

        .stack-footer a:hover {
            text-decoration: underline;
        }

        /* Loading */
        .stack-loading {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.95);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 16px;
            z-index: 100;
        }

        .stack-loading.active {
            display: flex;
        }

        .loading-spinner {
            width: 48px;
            height: 48px;
            border: 4px solid var(--stack-gray-200);
            border-top-color: var(--stack-purple);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        #loading-message {
            font-size: 14px;
            color: var(--stack-gray-500);
        }

        /* Responsive */
        @media (max-width: 440px) {
            .bonzi-stack-widget {
                border-radius: 0;
                max-width: none;
                min-height: 100vh;
            }
        }

        /* Modal Overlay (for floating/modal modes) */
        .stack-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999999;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s;
        }

        .stack-modal-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .stack-modal-content {
            position: relative;
            transform: scale(0.95);
            transition: transform 0.3s;
        }

        .stack-modal-overlay.active .stack-modal-content {
            transform: scale(1);
        }

        .stack-modal-close {
            position: absolute;
            top: -40px;
            right: 0;
            width: 32px;
            height: 32px;
            background: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        /* Floating Button */
        .stack-floating-btn {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(124, 58, 237, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999998;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .stack-floating-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5);
        }

        .stack-floating-btn svg {
            width: 28px;
            height: 28px;
        }
    `;

    // Inject CSS
    function injectStyles() {
        const style = document.createElement('style');
        style.textContent = WIDGET_CSS;
        document.head.appendChild(style);
    }

    // Load ethers.js if not present
    async function loadEthers() {
        if (typeof ethers !== 'undefined') return;

        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/ethers@6/dist/ethers.umd.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // Create widget container
    function createWidget() {
        const container = document.createElement('div');
        container.innerHTML = WIDGET_HTML;
        return container.firstElementChild;
    }

    // Show loading state
    function showLoading(message = 'Processing...') {
        const loading = document.getElementById('stack-loading');
        const loadingMsg = document.getElementById('loading-message');
        if (loading) {
            loadingMsg.textContent = message;
            loading.classList.add('active');
        }
    }

    // Hide loading state
    function hideLoading() {
        const loading = document.getElementById('stack-loading');
        if (loading) {
            loading.classList.remove('active');
        }
    }

    // Connect wallet
    async function connectWallet() {
        if (typeof window.ethereum === 'undefined') {
            alert('Please install MetaMask or another Web3 wallet to continue.');
            return false;
        }

        showLoading('Connecting wallet...');

        try {
            // Request accounts
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            address = accounts[0];

            // Create provider and signer
            provider = new ethers.BrowserProvider(window.ethereum);
            signer = await provider.getSigner();

            // Check network
            const network = await provider.getNetwork();
            if (Number(network.chainId) !== CONFIG.chainId) {
                try {
                    await window.ethereum.request({
                        method: 'wallet_switchEthereumChain',
                        params: [{ chainId: '0x1' }]
                    });
                } catch (switchError) {
                    hideLoading();
                    alert('Please switch to Ethereum Mainnet.');
                    return false;
                }
            }

            // Update UI
            const connectBtn = document.getElementById('stack-connect');
            connectBtn.textContent = address.slice(0, 6) + '...' + address.slice(-4);
            connectBtn.classList.add('connected');

            // Enable buttons
            document.getElementById('btn-stake').disabled = false;
            document.getElementById('btn-unstake').disabled = false;
            document.getElementById('btn-claim').disabled = false;

            // Load data
            await refreshData();

            hideLoading();
            return true;

        } catch (error) {
            console.error('Connect failed:', error);
            hideLoading();
            alert('Failed to connect wallet. Please try again.');
            return false;
        }
    }

    // Refresh all data
    async function refreshData() {
        if (!address || !provider) return;

        try {
            // Get token contract
            const token = new ethers.Contract(CONFIG.token, ABIS.ERC20, provider);
            const hardstake = new ethers.Contract(CONFIG.stakingContract, ABIS.HARDSTAKE, provider);

            // Get decimals
            const decimals = await token.decimals();

            // Get balances
            const balance = await token.balanceOf(address);
            const stakeInfo = await hardstake.stakes(address, CONFIG.token);
            const stakedAmount = stakeInfo.amount || stakeInfo[0] || 0n;
            const pendingRewards = await hardstake.pendingRewards(address, CONFIG.token);
            const totalStaked = await hardstake.totalStaked(CONFIG.token);

            // Format and display
            const formatTokens = (amount) => {
                const formatted = ethers.formatUnits(amount, decimals);
                const num = parseFloat(formatted);
                if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
                if (num >= 1000) return (num / 1000).toFixed(2) + 'K';
                return num.toFixed(2);
            };

            document.getElementById('stake-balance').textContent = formatTokens(balance) + ' ' + CONFIG.symbol;
            document.getElementById('stake-staked').textContent = formatTokens(stakedAmount) + ' ' + CONFIG.symbol;
            document.getElementById('total-staked').textContent = formatTokens(totalStaked) + ' ' + CONFIG.symbol;
            document.getElementById('rewards-pending').textContent = parseFloat(ethers.formatEther(pendingRewards)).toFixed(6);

        } catch (error) {
            console.error('Failed to refresh data:', error);
        }
    }

    // Stake tokens
    async function stakeTokens() {
        if (!signer || !address) {
            await connectWallet();
            return;
        }

        const amountInput = document.getElementById('stake-amount');
        const amount = amountInput.value;

        if (!amount || parseFloat(amount) <= 0) {
            alert('Please enter an amount to stake.');
            return;
        }

        showLoading('Preparing stake...');

        try {
            const token = new ethers.Contract(CONFIG.token, ABIS.ERC20, signer);
            const router = new ethers.Contract(CONFIG.router, ABIS.ROUTER, signer);
            const decimals = await token.decimals();
            const amountWei = ethers.parseUnits(amount, decimals);

            // Check allowance
            const allowance = await token.allowance(address, CONFIG.router);

            if (allowance < amountWei) {
                showLoading('Approving tokens...');
                const approveTx = await token.approve(CONFIG.router, ethers.MaxUint256);
                await approveTx.wait();
            }

            // Execute hardstake
            showLoading('Staking tokens...');
            const stakeTx = await router.hardstake(CONFIG.token, amountWei);
            await stakeTx.wait();

            // Refresh data
            amountInput.value = '';
            await refreshData();

            hideLoading();
            alert('Tokens staked successfully!');

        } catch (error) {
            console.error('Stake failed:', error);
            hideLoading();

            if (error.code === 4001 || error.code === 'ACTION_REJECTED') {
                alert('Transaction cancelled.');
            } else {
                alert('Staking failed: ' + (error.reason || error.message || 'Unknown error'));
            }
        }
    }

    // Unstake tokens
    async function unstakeTokens() {
        if (!signer || !address) {
            await connectWallet();
            return;
        }

        const amountInput = document.getElementById('stake-amount');
        const amount = amountInput.value;

        if (!amount || parseFloat(amount) <= 0) {
            alert('Please enter an amount to unstake.');
            return;
        }

        showLoading('Unstaking tokens...');

        try {
            const token = new ethers.Contract(CONFIG.token, ABIS.ERC20, provider);
            const router = new ethers.Contract(CONFIG.router, ABIS.ROUTER, signer);
            const decimals = await token.decimals();
            const amountWei = ethers.parseUnits(amount, decimals);

            const unstakeTx = await router.unstake(CONFIG.token, amountWei);
            await unstakeTx.wait();

            amountInput.value = '';
            await refreshData();

            hideLoading();
            alert('Tokens unstaked successfully!');

        } catch (error) {
            console.error('Unstake failed:', error);
            hideLoading();

            if (error.code === 4001 || error.code === 'ACTION_REJECTED') {
                alert('Transaction cancelled.');
            } else {
                alert('Unstaking failed: ' + (error.reason || error.message || 'Unknown error'));
            }
        }
    }

    // Claim rewards
    async function claimRewards() {
        if (!signer || !address) {
            await connectWallet();
            return;
        }

        showLoading('Claiming rewards...');

        try {
            const hardstake = new ethers.Contract(CONFIG.stakingContract, ABIS.HARDSTAKE, signer);

            const claimTx = await hardstake.claim(CONFIG.token);
            await claimTx.wait();

            await refreshData();

            hideLoading();
            alert('Rewards claimed successfully!');

        } catch (error) {
            console.error('Claim failed:', error);
            hideLoading();

            if (error.code === 4001 || error.code === 'ACTION_REJECTED') {
                alert('Transaction cancelled.');
            } else {
                alert('Claim failed: ' + (error.reason || error.message || 'Unknown error'));
            }
        }
    }

    // Set max amount for staking
    async function setMaxStakeAmount() {
        if (!address || !provider) {
            alert('Please connect your wallet first.');
            return;
        }

        try {
            const token = new ethers.Contract(CONFIG.token, ABIS.ERC20, provider);
            const balance = await token.balanceOf(address);
            const decimals = await token.decimals();
            const formatted = ethers.formatUnits(balance, decimals);

            document.getElementById('stake-amount').value = formatted;
        } catch (error) {
            console.error('Failed to get max amount:', error);
        }
    }

    // Switch tabs
    function switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.stack-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });

        // Update panels
        document.querySelectorAll('.stack-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === 'panel-' + tabName);
        });

        currentTab = tabName;

        // Refresh data when switching to stake/earn
        if ((tabName === 'stake' || tabName === 'earn') && address) {
            refreshData();
        }
    }

    // Bind events
    function bindEvents() {
        // Connect button
        document.getElementById('stack-connect').addEventListener('click', connectWallet);

        // Tab switching
        document.querySelectorAll('.stack-tab').forEach(tab => {
            tab.addEventListener('click', () => switchTab(tab.dataset.tab));
        });

        // Stake actions
        document.getElementById('btn-stake').addEventListener('click', stakeTokens);
        document.getElementById('btn-unstake').addEventListener('click', unstakeTokens);
        document.getElementById('stake-max').addEventListener('click', setMaxStakeAmount);

        // Claim
        document.getElementById('btn-claim').addEventListener('click', claimRewards);

        // Listen for account changes
        if (window.ethereum) {
            window.ethereum.on('accountsChanged', (accounts) => {
                if (accounts.length === 0) {
                    address = null;
                    signer = null;
                    const connectBtn = document.getElementById('stack-connect');
                    connectBtn.textContent = 'Connect Wallet';
                    connectBtn.classList.remove('connected');
                } else {
                    address = accounts[0];
                    const connectBtn = document.getElementById('stack-connect');
                    connectBtn.textContent = address.slice(0, 6) + '...' + address.slice(-4);
                    refreshData();
                }
            });

            window.ethereum.on('chainChanged', () => {
                window.location.reload();
            });
        }
    }

    // Create modal for modal/floating modes
    function createModal(widget) {
        const overlay = document.createElement('div');
        overlay.className = 'stack-modal-overlay';

        const content = document.createElement('div');
        content.className = 'stack-modal-content';

        const closeBtn = document.createElement('button');
        closeBtn.className = 'stack-modal-close';
        closeBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
        `;
        closeBtn.addEventListener('click', () => overlay.classList.remove('active'));

        content.appendChild(closeBtn);
        content.appendChild(widget);
        overlay.appendChild(content);

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.classList.remove('active');
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') overlay.classList.remove('active');
        });

        return overlay;
    }

    // Create floating button
    function createFloatingButton(onClick) {
        const btn = document.createElement('button');
        btn.className = 'stack-floating-btn';
        btn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
            </svg>
        `;
        btn.addEventListener('click', onClick);
        return btn;
    }

    // Initialize
    async function init() {
        injectStyles();
        await loadEthers();

        const widget = createWidget();

        if (CONFIG.mode === 'modal') {
            const modal = createModal(widget);
            document.body.appendChild(modal);

            // Create trigger button
            const triggerBtn = document.createElement('button');
            triggerBtn.className = 'stack-btn primary';
            triggerBtn.textContent = 'Buy + Stake + Earn';
            triggerBtn.style.cssText = 'max-width: 200px;';
            triggerBtn.addEventListener('click', () => modal.classList.add('active'));

            if (CONFIG.container) {
                document.getElementById(CONFIG.container).appendChild(triggerBtn);
            } else {
                currentScript.parentNode.insertBefore(triggerBtn, currentScript.nextSibling);
            }

        } else if (CONFIG.mode === 'floating') {
            const modal = createModal(widget);
            document.body.appendChild(modal);

            const floatingBtn = createFloatingButton(() => modal.classList.add('active'));
            document.body.appendChild(floatingBtn);

        } else {
            // Inline mode
            if (CONFIG.container) {
                document.getElementById(CONFIG.container).appendChild(widget);
            } else {
                currentScript.parentNode.insertBefore(widget, currentScript.nextSibling);
            }
        }

        bindEvents();
    }

    // Public API
    window.BonziStack = {
        open: function() {
            const modal = document.querySelector('.stack-modal-overlay');
            if (modal) modal.classList.add('active');
        },
        close: function() {
            const modal = document.querySelector('.stack-modal-overlay');
            if (modal) modal.classList.remove('active');
        },
        switchTab: switchTab,
        refresh: refreshData,
        connect: connectWallet,
        config: CONFIG
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
