# x402-go Audit — July 14, 2026

## Target

**Repo**: `github.com/mark3labs/x402-go`  
**Package**: `github.com/mark3labs/x402-go/v2`  
**Go version**: 1.25.1  
**Build**: ✅ passes  
**Tests**: ✅ all 14 sub-packages pass  

## Architecture

The repo has a clean **dual-package layout**: root package (`x402`) is v1, `v2/` subdirectory is v2. They share no types or implementations — completely independent.

### v2 Package Structure

```
v2/
├── chains.go          # CAIP-2 network identifiers + chain configs
├── config.go          # timeout config
├── errors.go          # sentinel errors + PaymentError (typed)
├── events.go          # payment callback events
├── selector.go        # DefaultPaymentSelector (multi-signer priority sort)
├── signer.go          # Signer interface
├── types.go           # core v2 types + AmountToBigInt helpers
├── validation/        # address, network, amount, payload validation
├── encoding/          # base64+JSON encode/decode for headers
├── facilitator/       # Interface (Verify/Settle/Supported)
├── http/              # middleware, transport, client, facilitator client
│   ├── gin/           # Gin framework wrapper
├── mcp/               # MCP server + client wrappers
├── signers/evm/       # EIP-3009 EVM signer
├── signers/svm/       # Solana SVM signer
└── internal/          # eip3009, solana helpers
```

## Per-Criterion Compliance

### 1. PaymentRequired — `x402Version` field ✅

```go
type PaymentRequired struct {
    X402Version int                  `json:"x402Version"`  // constant 2
    Error       string               `json:"error,omitempty"`
    Resource    *ResourceInfo        `json:"resource,omitempty"`
    Accepts     []PaymentRequirements `json:"accepts"`
    Extensions  map[string]Extension `json:"extensions,omitempty"`
}
```

- `x402Version` is a JSON number (`2`), not a string — matches spec
- `PaymentRequirements` has `scheme` (string, e.g. `"exact"`), `network` (CAIP-2), `amount` (string, atomic units), `asset`, `payTo`, `maxTimeoutSeconds`, `extra` (map for EIP-3009 params)

**Verdict**: Fully spec-compliant.

### 2. Header Encoding — base64 + JSON ✅

```go
// v2/encoding/encoding.go
func EncodePayment(payment v2.PaymentPayload) (string, error) {
    paymentJSON, _ := json.Marshal(payment)
    return base64.StdEncoding.EncodeToString(paymentJSON), nil
}
```

- Uses standard base64 (not URL-safe or hex) — correct per spec
- Supports: `EncodePayment`, `DecodePayment`, `EncodeSettlement`, `DecodeSettlement`, `EncodeRequirements`, `DecodeRequirements`, `EncodeVerifyResponse`, `DecodeVerifyResponse`
- Headers: `X-PAYMENT` (client→server) and `X-PAYMENT-RESPONSE` (server→client)

**Verdict**: Correct. No issues.

### 3. HTTP Middleware — 402 gating ✅

- `NewX402Middleware(config)` returns `func(http.Handler) http.Handler`
- Flow: check `X-PAYMENT` header → parse → find matching requirement → facilitator `/verify` → on success, serve handler → on 2xx response, facilitator `/settle`
- `settlementInterceptor` wraps `ResponseWriter` for deferred settlement (commits only on status < 400)
- Dual-fallback facilitator support, auth providers, lifecycle hooks
- Gin wrapper at `v2/http/gin/middleware.go`

**Verdict**: Full production-grade middleware.

### 4. Client — auto-pay on 402 ✅

- `X402Transport` implements `http.RoundTripper`
- On 402: parses body → selects signer via `PaymentSelector` → signs → retries with `X-PAYMENT` header → parses `X-PAYMENT-RESPONSE` from response
- Multi-signer selection: priority sort (signer → token → config order)
- Max-amount limits per signer
- Payment callbacks (`OnPaymentAttempt`, `OnPaymentSuccess`, `OnPaymentFailure`)

**Verdict**: Complete client implementation.

### 5. CAIP-2 Network Identifiers ✅

```go
const (
    NetworkBase      = "eip155:8453"
    NetworkPolygon   = "eip155:137"
    NetworkEthereum  = "eip155:1"
    NetworkSolanaMainnet = "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp"
)
```

- `ValidateNetwork()` requires exactly `namespace:reference` format
- `eip155` namespace: validates reference is a numeric chain ID (`strconv.ParseInt`)
- `solana` namespace: validates reference is 32-44 chars (genesis hash length)
- Unknown namespaces return `NetworkTypeUnknown` error

**Verdict**: Proper CAIP-2 with validation.

### 6. Asset Addresses — Lowercase Hex ⚠️

**Problem**: The default chain configs use **checksummed (mixed-case)** EVM addresses:

```go
BaseMainnet = ChainConfig{
    USDCAddress: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  // mixed case!
}
```

**Evidence**:
- All 8 EVM chain configs use checksummed addresses (verified by inspecting `v2/chains.go`)
- Validation regex: `^0x[a-fA-F0-9]{40}$` — accepts both cases (correct for acceptance)
- Address matching: `strings.EqualFold` in `CanSign()` — case-insensitive (correct for internal use)
- **Wire format**: When serialized to JSON, the address goes out as-is (mixed-case)

**Impact**: Low. Works internally (case-insensitive everywhere). Risk only with strict downstream validators that reject non-lowercase hex addresses.

**Fix**: Lowercase all `USDCAddress` constants, or add `strings.ToLower()` at marshal time.

### 7. `/.well-known/x402` Discovery ❌

**No implementation exists**. Searched "well-known", "wellknown", and ".well-known" across the entire codebase. Only match is an unrelated comment about "well-known test keys" in test files.

**Impact**: Servers using this library have no standard way to advertise payment capabilities. This is the same gap as the x402-rs (Rust) SDK.

**Fix**: Add a handler helper function that generates the standard discovery response.

### 8. MCP Integration ✅

- `v2/mcp/server/`: `X402Server` wraps an MCP server with per-tool payment gating
- `AddPayableTool()` registers a paid tool with resource info and payment requirements
- `AddTool()` registers a free tool (no payment)
- Payment is passed in `_meta.x402/payment` field of JSON-RPC params (not HTTP headers)
- Settlement response injected into `result._meta["x402/payment-response"]`
- Same facilitator verify/settle flow as HTTP middleware

**Verdict**: Complete and spec-aligned.

### 9. Signers — EVM (EIP-3009) ✅

- Full `transferWithAuthorization` flow
- EIP-3009 domain parameters (`name`, `version`) from `Extra` map in payment requirements
- `CreateAuthorization()`: generates validAfter/validBefore, nonce
- `SignAuthorization()`: EIP-712 typed data signing
- Chain ID extracted from CAIP-2 network (e.g., `eip155:8453` → 8453)

### 10. Signers — SVM (Solana) ✅

- Partially-signed SPL token transfer via `TransferChecked` instruction
- Fee payer specified in `Extra["feePayer"]`
- Client signs, facilitator completes (adds fee payer signature)
- Blockhash fetched from network RPC
- Destination ATA created idempotently

## Summary Table

| Criterion | Status | Notes |
|-----------|--------|-------|
| `x402Version: 2` (int) | ✅ | |
| `scheme: "exact"` | ✅ | |
| `payTo` (not `payment_address`) | ✅ | |
| Encoding: base64+JSON | ✅ | |
| HTTP middleware (net/http) | ✅ | + Gin wrapper |
| HTTP client (auto-pay) | ✅ | |
| CAIP-2 network format | ✅ | |
| Asset addresses lowercase hex | ⚠️ | Mixed-case defaults; works internally |
| `/.well-known/x402` | ❌ | Not implemented |
| `accepts` array format | ✅ | |
| Extension support | ✅ | Extension type present |
| EVM signer (EIP-3009) | ✅ | |
| SVM signer (Solana) | ✅ | |
| MCP integration | ✅ | |
| All packages compile | ✅ | |
| All v2 tests pass | ✅ | |

**Bottom line**: Solid production-quality implementation. Two gaps: (1) no `/.well-known/x402` discovery, (2) checksummed default asset addresses instead of lowercase hex.
