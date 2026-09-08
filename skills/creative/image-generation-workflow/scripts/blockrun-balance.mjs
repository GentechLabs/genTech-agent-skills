// BlockRun Base USDC balance — on-chain read.
// client.getBalance() is broken ("not a function") in the installed
// /root/.hermes/blockrun-mcp build, so read USDC directly via eth_call.
// Run: node /root/.hermes/blockrun-mcp/blockrun-balance.mjs
const usdc = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
const wallet = '0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8';
const rpc = 'https://mainnet.base.org';
const data = '0x70a08231000000000000000000000000' + wallet.slice(2).toLowerCase();
const r = await fetch(rpc, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to: usdc, data }, 'latest'] }) });
const j = await r.json();
const bal = parseInt(j.result, 16) / 1e6;
console.log(`USDC on Base: $${bal.toFixed(2)}`);
