/**
 * Paste into DevTools console on stake-tg.html (or any page with ethers@5 + window.ethereum).
 * Mainnet only. Read-only except eth_requestAccounts.
 *
 * Addresses match community-bot/stake-tg.html CONTRACTS.
 */
async function checkContractAuthorization() {
    if (typeof ethers === 'undefined') {
        return { success: false, message: 'ethers not on window — open stake-tg.html first' };
    }
    if (!window.ethereum || typeof window.ethereum.request !== 'function') {
        return { success: false, message: 'No injected wallet (window.ethereum)' };
    }

    const CHAIN_ID_HEX = '0x1';
    const ROUTER = '0x9bD63C5D44fF28390df1EaaFD4eB4BD73E94A72a';
    const BONZI_TOKEN = '0xd6175692026bcd7cb12a515e39cf0256ef35cb86';
    const BONZI_HARDSTAKE = '0x3618158bb8d07111e476f4de28676dff050d1a53';

    const data = {
        userAddress: null,
        chainId: null,
        results: [],
        hardstakeStaticCall: null
    };

    try {
        data.chainId = await window.ethereum.request({ method: 'eth_chainId' });
        if (String(data.chainId).toLowerCase() !== CHAIN_ID_HEX) {
            return {
                success: false,
                message: 'Switch wallet to Ethereum mainnet (chainId 0x1). Got: ' + data.chainId,
                data
            };
        }

        const provider = new ethers.providers.Web3Provider(window.ethereum, 'any');
        const signer = provider.getSigner();
        data.userAddress = await signer.getAddress();

        const targetContracts = [
            { name: 'BONZI token (ERC-20)', address: BONZI_TOKEN },
            { name: 'EtherVista / Euler router', address: ROUTER },
            { name: 'BONZI hardstake pool', address: BONZI_HARDSTAKE }
        ];

        const probeAbi = [
            'function isAuthorized(address) view returns (bool)',
            'function restricted(address) view returns (bool)',
            'function isRestricted(address) view returns (bool)',
            'function owner() view returns (address)'
        ];

        for (const contractInfo of targetContracts) {
            const contract = new ethers.Contract(contractInfo.address, probeAbi, provider);
            const report = { name: contractInfo.name, address: contractInfo.address };
            try {
                report.isAuthorized = await contract.isAuthorized(data.userAddress);
            } catch (e) {
                report.isAuthorized_error = (e && e.reason) || e.message || String(e);
            }
            try {
                report.restricted = await contract.restricted(data.userAddress);
            } catch (e) {
                report.restricted_error = (e && e.reason) || e.message || String(e);
            }
            try {
                report.isRestricted = await contract.isRestricted(data.userAddress);
            } catch (e) {
                report.isRestricted_error = (e && e.reason) || e.message || String(e);
            }
            try {
                report.owner = await contract.owner();
            } catch (e) {
                report.owner_error = (e && e.reason) || e.message || String(e);
            }
            data.results.push(report);
        }

        const routerIface = new ethers.utils.Interface([
            'function hardstake(address _contract, address _token, uint256 _amount)'
        ]);
        const probeAmount = ethers.BigNumber.from('1');
        const calldata = routerIface.encodeFunctionData('hardstake', [
            BONZI_HARDSTAKE,
            BONZI_TOKEN,
            probeAmount
        ]);

        try {
            await provider.call({
                to: ROUTER,
                from: data.userAddress,
                data: calldata
            });
            data.hardstakeStaticCall = { ok: true, note: 'call returned (unexpected for tiny amount — check allowance)' };
        } catch (e) {
            data.hardstakeStaticCall = {
                ok: false,
                revert: (e && e.reason) || e.message || String(e),
                data: e && e.data ? e.data : undefined
            };
        }

        return { success: true, data };
    } catch (err) {
        return { success: false, error: err && err.message ? err.message : String(err) };
    }
}

// await checkContractAuthorization();
