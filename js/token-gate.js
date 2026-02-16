// Token-gated access for BONZI/VISTA whitepaper
// Client-side wallet connect + balance check

const TOKEN_ADDRESSES = {
    BONZI: '0x1c6E06e07257B1d2FF8AeD2930F8aaB650877260',
    VISTA: '0x0F1f0E8b8093CD5002BD9C9596F6Ce877fD5DB04'
};

const TOKEN_ABI = [
    {
        "constant": true,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
];

class TokenGate {
    constructor() {
        this.provider = null;
        this.walletAddress = null;
        this.accessGranted = false;
    }

    async init() {
        // Check if already connected (from localStorage with 24h expiry)
        const savedWallet = localStorage.getItem('token_gate_wallet');
        const savedAccess = localStorage.getItem('token_gate_access');
        const savedTimestamp = localStorage.getItem('token_gate_timestamp');
        const isValid = savedWallet && savedAccess === 'granted' && savedTimestamp &&
                       (Date.now() - parseInt(savedTimestamp)) < 24 * 60 * 60 * 1000;

        if (isValid) {
            // Skip gate, access already granted within 24h
            const overlay = document.getElementById('token-gate-overlay');
            if (overlay) {
                overlay.style.display = 'none';
            }
            document.body.classList.add('access-granted');
        } else {
            this.showConnectOverlay();
        }
    }

    showConnectOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'token-gate-overlay';
        overlay.innerHTML = `
            <div class="token-gate-modal">
                <div class="token-gate-header">
                    <img src="/bonzi-logo.png" alt="Bonzi" style="width: 48px; height: 48px; border-radius: 50%;">
                    <h2>Holder Access Required</h2>
                </div>
                <p>This whitepaper is exclusive to BONZI and VISTA token holders.</p>
                <p style="font-size: 14px; color: #71717A; margin-top: 12px;">
                    Connect your wallet to verify ownership. No gas fees required.
                </p>
                <button id="connect-wallet-btn" class="token-gate-btn">
                    Connect Wallet
                </button>
                <div id="token-gate-status" style="margin-top: 16px; font-size: 13px; color: #71717A;"></div>
            </div>
        `;
        document.body.appendChild(overlay);

        document.getElementById('connect-wallet-btn').addEventListener('click', () => {
            this.connectWallet();
        });
    }

    async connectWallet() {
        const statusDiv = document.getElementById('token-gate-status');
        statusDiv.textContent = 'Connecting...';

        try {
            // Check if MetaMask is installed
            if (typeof window.ethereum === 'undefined') {
                statusDiv.innerHTML = '⚠️ MetaMask not detected. <a href="https://metamask.io" target="_blank" rel="noopener noreferrer" style="color: #7C3AED;">Install MetaMask</a>';
                return;
            }

            // Request account access
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            this.walletAddress = accounts[0];

            // Check network
            const chainId = await window.ethereum.request({ method: 'eth_chainId' });
            if (chainId !== '0x1') {
                statusDiv.textContent = '⚠️ Switch to Ethereum Mainnet';
                return;
            }

            statusDiv.textContent = 'Checking token balance...';

            // Check if user holds BONZI or VISTA
            await this.checkAccess();

        } catch (error) {
            console.error('Wallet connection error:', error);
            statusDiv.textContent = '❌ Connection failed. Try again.';
        }
    }

    async checkAccess() {
        const statusDiv = document.getElementById('token-gate-status');

        try {
            // Use Infura or Alchemy as provider
            const provider = new ethers.providers.Web3Provider(window.ethereum);

            // Check BONZI balance (need ≥1M tokens = 1e24 wei for 18 decimals)
            const bonziContract = new ethers.Contract(TOKEN_ADDRESSES.BONZI, TOKEN_ABI, provider);
            const bonziBalance = await bonziContract.balanceOf(this.walletAddress);
            const bonziMin = ethers.BigNumber.from('1000000').mul(ethers.BigNumber.from('10').pow(18));

            // Check VISTA balance (need any amount)
            const vistaContract = new ethers.Contract(TOKEN_ADDRESSES.VISTA, TOKEN_ABI, provider);
            const vistaBalance = await vistaContract.balanceOf(this.walletAddress);

            const hasBonzi = bonziBalance.gte(bonziMin);
            const hasVista = vistaBalance.gt(0);

            if (hasBonzi || hasVista) {
                // Access granted
                this.accessGranted = true;
                localStorage.setItem('token_gate_wallet', this.walletAddress);
                localStorage.setItem('token_gate_access', 'granted');
                localStorage.setItem('token_gate_timestamp', Date.now().toString());

                // Log access event (GDPR-friendly - no PII, just wallet + timestamp)
                this.logAccess(hasBonzi ? 'BONZI' : 'VISTA');

                // Hide overlay and show content
                this.grantAccess();
            } else {
                // No tokens found
                if (statusDiv) {
                    statusDiv.innerHTML = `
                        ❌ Insufficient balance. Need 1M+ BONZI or any VISTA.
                        <br><br>
                        <a href="/" style="color: #7C3AED; text-decoration: none;">← Back to homepage</a>
                        <br>
                        <a href="/economics/#ethervista" style="color: #7C3AED; text-decoration: none;">How to buy →</a>
                    `;
                }
            }
        } catch (error) {
            console.error('Balance check error:', error);
            if (statusDiv) {
                statusDiv.textContent = '❌ Error checking balance. Try refreshing the page.';
            }
        }
    }

    logAccess(token) {
        // Log to Google Analytics or custom endpoint
        if (typeof gtag !== 'undefined') {
            gtag('event', 'whitepaper_access', {
                'wallet': this.walletAddress.slice(0, 6) + '...' + this.walletAddress.slice(-4), // Anonymized
                'token': token,
                'timestamp': new Date().toISOString()
            });
        }

        // Could also POST to backend: /api/log-whitepaper-access
        // fetch('/api/log-whitepaper-access', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({
        //         wallet: this.walletAddress,
        //         token: token,
        //         timestamp: Date.now()
        //     })
        // });
    }

    grantAccess() {
        const overlay = document.getElementById('token-gate-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => overlay.remove(), 300);
        }

        // Show content (remove blur/hidden class)
        document.body.classList.add('access-granted');

        // Show success message
        const banner = document.createElement('div');
        banner.className = 'access-granted-banner';
        banner.innerHTML = '✓ Access granted - Welcome, holder!';
        document.body.appendChild(banner);
        setTimeout(() => banner.remove(), 3000);
    }
}

// Auto-init on whitepaper pages
if (window.location.pathname.includes('whitepaper')) {
    // Load ethers.js from CDN
    const script = document.createElement('script');
    script.src = 'https://cdn.ethers.io/lib/ethers-5.7.2.umd.min.js';
    script.onload = () => {
        const gate = new TokenGate();
        gate.init();
    };
    document.head.appendChild(script);
}
