# Paymenter x402 Gateway — Marketplace Integration Reference

## Platform Overview

**Paymenter** (1.9k ⭐, MIT) is an open-source billing platform for hosting companies. PHP/Laravel, Stripe integration, Pterodactyl integration, subscription management, extension marketplace.

- Website: https://paymenter.org
- GitHub: https://github.com/Paymenter/Paymenter
- Marketplace: https://paymenter.org/marketplace (227 extensions)
- Discord: https://discord.gg/paymenter-882318291014651924

## Market Gap

227 extensions on the marketplace. **Zero crypto gateways.** Every single one uses Stripe/PayPal.

## Our Extension

**Repo:** https://github.com/ProtoJay4789/paymenter-x402

The extension adds "Pay with Crypto (x402)" as a checkout option. When selected, it generates an x402 payment request with a QR code. On confirmation, the invoice is marked paid. Includes Q402 Trust Receipts for cryptographically signed settlement records.

### File Structure
```
extensions/Gateways/X402/
├── X402.php              # Gateway class (pay, canUseGateway, handleWebhook)
├── routes.php            # Webhook routes
├── resources/views/
│   └── pay.blade.php     # Checkout page with QR code + polling
├── composer.json         # Package definition
└── README.md             # Install guide
```

### Configuration Fields
- x402 Gateway URL (default: https://api.gentechlabs.net/x402)
- x402 API Key (optional)
- Merchant Wallet Address
- Blockchain Network (Solana, Base, Ethereum, Polygon)
- Accepted Token (USDC, USDT, SOL, ETH)

## Revenue Model

1. **Sell the extension** — $9.99-$24.99 on the marketplace
2. **Transaction fee** — 0.5% of every x402 payment processed through our gateway
3. **Network effect** — every hosting company that installs it becomes a node
4. **White-label** — "Powered by GenTech x402" on the checkout page

## Expansion

Same extension pattern works for:
- **WHMCS** — largest hosting billing platform (thousands of extensions)
- **Blesta** — growing alternative
- **HostBill** — enterprise hosting billing

## Submission Checklist

- [ ] Push to GitHub (MIT license) — DONE at ProtoJay4789/paymenter-x402
- [ ] Submit to Paymenter marketplace at paymenter.org/marketplace
- [ ] Post in Paymenter Discord community
- [ ] Cross-post to Pterodactyl community
- [ ] Build WHMCS version
- [ ] Build Blesta version
