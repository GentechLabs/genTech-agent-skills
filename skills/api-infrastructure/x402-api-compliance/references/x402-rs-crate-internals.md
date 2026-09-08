# x402-rs Crate Internals — Version Gap & Wire Format Details

## Version landscape (July 2026)

| Crate | Pinned in Marlin gateway | Latest published | Delta |
|-------|--------------------------|------------------|-------|
| `x402-axum` | 1.3.0 | 2.0.2 | V2 PaymentRequired missing `extensions` |
| `x402-chain-eip155` | 1.3.0 | 2.0.2 | API surface changes |
| `x402-chain-solana` | 1.3.0 | 2.0.2 | API surface changes |
| `x402-types` | 1.3.0 | 2.0.2 | Core type changes |
| `x402-reqwest` | 1.3.0 | 2.0.2 | Client-side changes |

The Marlin gateway (`marlinprotocol/x402-gateway`) pins all x402-rs crates at `"1.3"`. The latest is `2.0.2`.

## Critical difference: V2 `PaymentRequired` is missing `extensions` in 1.3.0

### 1.3.0 (`x402-types/src/proto/v2.rs`)
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PaymentRequired<TAccepts = PaymentRequirements> {
    pub x402_version: X402Version2,
    pub error: Option<String>,
    pub resource: ResourceInfo,
    pub accepts: Vec<TAccepts>,
}
```
No `extensions` field. No way to advertise protocol extensions (Bazaar, fee payer, etc.).

### 2.0.2 (`x402-axum/paygate.rs`)
The `error_into_response` method constructs:
```rust
let payment_required_response = v2::PaymentRequired {
    error: Some(err.to_string()),
    accepts: accepts.iter().map(|pt| pt.requirements.clone()).collect(),
    x402_version: v2::X402Version2,
    resource: Some(resource.clone()),
    extensions: extensions.clone(),  // ← ADDED in 2.x
};
```
The 2.x `X402Middleware` and `X402LayerBuilder` expose `with_extension()` to populate this. Gateways on 1.3.0 cannot advertise extensions at all.

## Wire format: V1 PaymentRequirements vs V2 PaymentRequirements

Both enumerated from the actual `x402-types` v1.3.0 source code.

### V1 `PaymentRequirements` (sent inline in 402 response body)
```rust
pub struct PaymentRequirements {
    pub scheme: String,                  // e.g. "exact"
    pub network: String,                 // e.g. "base-sepolia" (human name, NOT CAIP-2)
    pub max_amount_required: String,     // ← V1 field name (not "amount"!)
    pub resource: String,                // ← inline URL
    pub description: String,             // ← inline description
    pub mime_type: Option<String>,       // ← inline MIME
    pub output_schema: Option<String>,   // ← V1 only
    pub pay_to: String,
    pub max_timeout_seconds: u64,
    pub asset: String,
    pub extra: Option<Value>,
}
```

### V2 `PaymentRequirements` (in `PaymentRequired.accepts[]`)
```rust
pub struct PaymentRequirements {
    pub scheme: String,                  // e.g. "exact"
    pub network: ChainId,                // ← CAIP-2 (e.g. "eip155:8453")
    pub amount: String,                  // ← short name (not "maxAmountRequired")
    pub pay_to: String,
    pub max_timeout_seconds: u64,
    pub asset: String,
    pub extra: Option<Value>,
}
```

### V2 `PaymentRequired` (base64-encoded in `Payment-Required` header)
```rust
pub struct PaymentRequired {
    pub x402_version: X402Version2,      // serializes as integer 2
    pub error: Option<String>,
    pub resource: ResourceInfo,           // ← top-level, not inline
    pub accepts: Vec<PaymentRequirements>,
}
```

### V2 `ResourceInfo`
```rust
pub struct ResourceInfo {
    pub description: String,
    pub mime_type: String,
    pub url: String,
}
```

### Key structural differences

| Concern | V1 | V2 |
|---------|----|----|
| Amount field | `maxAmountRequired` | `amount` |
| Network format | Network name string (e.g. `"base-sepolia"`) | CAIP-2 chain ID (e.g. `"eip155:8453"`) |
| Resource metadata | Inline in each `PaymentRequirements` (`resource`, `description`, `mime_type`, `output_schema`) | Top-level `ResourceInfo` in `PaymentRequired` |
| 402 response body | Full JSON body | Empty body (JSON goes in `Payment-Required` header, base64-encoded) |
| Incoming payment header | `X-PAYMENT` | `Payment-Signature` |
| Extensions | N/A | `extensions` block (2.x only) |
| `output_schema` | Present | Removed |

## Incoming payment header: V1 vs V2

The header name is set per-protocol in `PaygateProtocol::PAYMENT_HEADER_NAME`:

```rust
// x402_axum::paygate.rs — V1
impl PaygateProtocol for v1::PriceTag {
    const PAYMENT_HEADER_NAME: &'static str = "X-PAYMENT";
    // ...
}

// x402_axum::paygate.rs — V2
impl PaygateProtocol for v2::PriceTag {
    const PAYMENT_HEADER_NAME: &'static str = "Payment-Signature";
    // ...
}
```

The Marlin gateway uses `V2Eip155Exact` and `V2SolanaExact` price tags, which are V2 types, so it reads `Payment-Signature` and sends `Payment-Required`. The deprecated `X-PAYMENT` header is never emitted.

## How the Marlin gateway uses the crate

From `src/pricing.rs`:
```rust
use x402_types::{networks::USDC, proto::v2::PriceTag as V2PriceTag};
// ...
V2Eip155Exact::price_tag(address, usdc.amount(usdc_amount))
V2SolanaExact::price_tag(solana_addr, usdc.amount(usdc_amount))
```

From `src/main.rs`:
```rust
let x402 = X402Middleware::try_from(config.facilitator_url.as_str())?;
let layer = build_price_layer(&x402, &config.networks, route_config.usdc_amount);
app = app.route(&route_config.path, any(proxy_request).layer(layer));
```

The middleware catches unauthenticated requests, generates the 402 V2 response with the `Payment-Required` header, and never calls the handler. On valid Payment-Signature, it calls the handler which proxies to the target API.

## Enrichment mechanism

The x402-rs crate calls `enrich_accepts()` on the `Paygate` struct during middleware initialization (line 484 of 2.x `layer.rs`). This calls the facilitator's `/supported` endpoint and enriches each price tag with facilitator capabilities (fee payer info, etc.). The enrichment is transparent to the gateway application but important — without a working facilitator, the 402 response may lack gateway/facilitator metadata that clients need.

## Config-to-protocol field mapping in Marlin gateway

| Config field | Config example | Maps to (via crate) | Wire field |
|---|---|---|---|
| `payment_address` | `"0xYOUR_EVM_ADDRESS"` | `V2Eip155Exact::price_tag(address, ...)` | `payTo` |
| `network` | `"base-sepolia"` | `USDC::base_sepolia()` | `network: "eip155:84532"` (CAIP-2, auto-converted) |
| `usdc_amount` | `1000` | `usdc.amount(1000)` | `amount: "1000"` |

The config field `payment_address` is **not** the V1 protocol field name — both V1 and V2 use `payTo` (`pay_to` in Rust). The config just uses a different internal name. No V1 field names leak into the wire format.
