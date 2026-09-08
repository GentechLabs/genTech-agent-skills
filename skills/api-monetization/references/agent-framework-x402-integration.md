# x402 Integration into Agent Framework Auth Systems

How to add x402 (HTTP 402 Payment Required) as a custom authentication scheme to external agent frameworks that support pluggable auth.

## General Pattern

The pattern works for any framework with:
- A typed auth scheme model (describes *what* auth is needed)
- An abstract auth provider (handles *how* to fulfill it)
- A registry that maps scheme types to providers

```
CustomAuthScheme (describes payment params)
    → chain, token, amount, recipient, price_feed, max_retries

BaseAuthProvider (implements signing flow)
    → takes signing_callback (wallet-agnostic)
    → get_auth_credential() → signed HTTP credential

AuthProviderRegistry (wires scheme → provider)
    → scheme auto-routes to provider at runtime
```

## Architecture Decisions

1. **Signing callback pattern** — The provider takes a callback function rather than handling signing itself. This keeps the framework core clean and allows users to inject any wallet: EOA, smart wallet, hardware, KMS, or agent wallet. The callback receives the auth scheme (payment params) and returns a signed payload.

2. **HTTP credential format** — Return the signed proof as an HTTP auth credential with a custom scheme (`PAYMENT-SIGNATURE`) and additional metadata headers (`X-P402-Chain`, `X-P402-Token`, `X-P402-Amount`, etc.). This integrates naturally with existing HTTP auth handling in the framework.

3. **Credential reuse** — Check for existing exchanged credentials before re-signing. If the provider already has a valid credential, return it. Saves signing cost on repeated calls.

4. **Graceful failure** — Return `None` (not throw) when signing fails. The framework should handle the absence of credentials.

## Google ADK Implementation (shipped Jul 2026)

Files:
- `src/google/adk/auth/x402_auth_scheme.py` — `X402AuthScheme(CustomAuthScheme)`
- `src/google/adk/auth/x402_auth_provider.py` — `X402AuthProvider(BaseAuthProvider)`
- `tests/unittests/auth/test_x402_auth.py` — 8 tests, all passing

### Scheme fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| chain | str | "base" | Target blockchain |
| token | str | "USDC" | Token symbol |
| amount | str | None | Per-call amount (decimal) |
| recipient | str | None | Payment recipient address |
| rpc_url | str | None | Custom RPC URL override |
| price_feed | str | None | Dynamic pricing contract |
| max_retries | int | 3 | Retry limit |

### Signing callback signature

```python
# Callback receives scheme → returns signed payload or None
SigningCallback = Callable[[X402AuthScheme], X402SignedPayload | None]

# Payload shape
class X402SignedPayload:
    signature: str       # Hex ECDSA signature
    payment_hash: str    # Hash of payment params
    chain: str
    token: str
    amount: str
    recipient: str
    timestamp: int
    expires_at: int | None
```

### Provider output

Returns `AuthCredential` with:
- `http.scheme = "PAYMENT-SIGNATURE"`
- `http.credentials.token = "x402 {sig} {hash}"`
- `http.additional_headers` with chain, token, amount, recipient, timestamp, payment_hash

### Registration

```python
from google.adk.auth import AuthProviderRegistry
from google.adk.auth.x402_auth_scheme import X402AuthScheme
from google.adk.auth.x402_auth_provider import X402AuthProvider

def my_signer(scheme: X402AuthScheme) -> X402SignedPayload | None:
    # Implement wallet signing here
    ...

registry = AuthProviderRegistry()
provider = X402AuthProvider(signing_callback=my_signer)
registry.register(X402AuthScheme, provider)
```

## Adapting to Other Frameworks

Look for these extension points in the target framework:

1. **Custom scheme type** — Can you define a new auth scheme class that extends an existing base? Frameworks with OpenAPI-based auth (OAuth2, API Key, etc.) often have a custom scheme escape hatch.

2. **Auth provider interface** — Is there an abstract class where you implement `get_credential()` or similar? You need to return the x402 signed proof in the format the framework's HTTP client expects (usually a header).

3. **Registry pattern** — How does the framework route auth type → auth handler? You need to register your custom scheme there.

Common integration points across frameworks:
- FastAPI/Starlette: `route.dependencies` + middleware
- LangChain: custom `CallbackHandler` or `tool` wrapper
- OpenAI: function calling with payment headers
- MCP: `_meta["x402/payment"]` in tool response
- Claude Code: skill-based payment injection
