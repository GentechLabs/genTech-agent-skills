# OpenAPI ENDPOINT_META Pattern — x402 Gateway Reference

Full working implementation from the GenTech x402 gateway (15 endpoints, deployed at `api.gentechlabs.net`).

## Architecture

Replace the old generic route-loop OpenAPI generator with a **per-endpoint metadata map**. The generator reads from a `Record<string, EndpointMeta>` that describes each endpoint's method, parameters, request body, and descriptions — all with real-world examples that x402scan's discovery tool (`@agentcash/discovery`) uses to construct valid probe requests.

## Interface

```typescript
interface EndpointMeta {
  method: 'get' | 'post';
  summary: string;
  description: string;
  queryParams?: { name: string; type: string; description: string; example?: string | number; required?: boolean }[];
  pathParams?: { name: string; type: string; description: string; example?: string }[];
  requestBody?: {
    required?: boolean;
    properties: { name: string; type: string; description: string; example: any; required?: boolean }[];
  };
}
```

## ENDPOINT_META (all 15 endpoints)

```typescript
const ENDPOINT_META: Record<string, EndpointMeta> = {
  '/v1/games/search': {
    method: 'get',
    summary: 'Search for game deals across stores',
    description: 'Search for the cheapest game deals across multiple stores. Returns title, sale price, normal price, store, and deal rating.',
    queryParams: [{ name: 'title', type: 'string', description: 'Game title to search for', example: 'Cyberpunk 2077', required: true }],
  },
  '/v1/games/cheapest': {
    method: 'get',
    summary: 'Get cheapest games on sale',
    description: 'List the cheapest game deals currently available. Filter by store, price range, or metacritic rating.',
    queryParams: [
      { name: 'store', type: 'string', description: 'Store filter (e.g. Steam, Epic, GOG)', example: 'Steam', required: false },
      { name: 'maxPrice', type: 'number', description: 'Maximum price in USD', example: 9.99, required: false },
    ],
  },
  '/v1/games/{id}/news': {
    method: 'get',
    summary: 'Get latest news for a game',
    description: 'Get the latest news articles, updates, and announcements for a specific game by its deal ID.',
    pathParams: [{ name: 'id', type: 'string', description: 'Game deal ID', example: 'MjE1NTE5' }],
  },
  '/v1/games/{id}/release': {
    method: 'get',
    summary: 'Get game release date info',
    description: 'Get release date, platforms, and availability information for a specific game.',
    pathParams: [{ name: 'id', type: 'string', description: 'Game deal ID', example: 'MjE1NTE5' }],
  },
  '/v1/movies/search': {
    method: 'get',
    summary: 'Search for movies and deals',
    description: 'Search for movies with available deals, including digital and physical copy pricing.',
    queryParams: [{ name: 'title', type: 'string', description: 'Movie title to search for', example: 'Dune: Part Two', required: true }],
  },
  '/v1/movies/cheapest': {
    method: 'get',
    summary: 'Get cheapest movies on sale',
    description: 'List the cheapest movie deals currently available across digital and physical retailers.',
    queryParams: [
      { name: 'genre', type: 'string', description: 'Movie genre filter', example: 'Sci-Fi', required: false },
      { name: 'maxPrice', type: 'number', description: 'Maximum price in USD', example: 14.99, required: false },
    ],
  },
  '/v1/movies/{id}/details': {
    method: 'get',
    summary: 'Get movie details',
    description: 'Get detailed information about a specific movie including synopsis, cast, runtime, and rating.',
    pathParams: [{ name: 'id', type: 'string', description: 'Movie deal ID', example: 'NzIwNjk=' }],
  },
  '/v1/movies/{id}/trailers': {
    method: 'get',
    summary: 'Get movie trailers',
    description: 'Get available trailers and video previews for a specific movie.',
    pathParams: [{ name: 'id', type: 'string', description: 'Movie deal ID', example: 'NzIwNjk=' }],
  },
  '/v1/intel/search': {
    method: 'get',
    summary: 'Market intelligence search',
    description: 'Search market intelligence data for trends, sentiment, and analysis across crypto and AI agent markets.',
    queryParams: [{ name: 'q', type: 'string', description: 'Search query for market intelligence', example: 'AI agent tokens', required: true }],
  },
  '/v1/intel/cheapest': {
    method: 'get',
    summary: 'Cheapest intelligence data',
    description: 'Get the cheapest available market intelligence data points and analysis snippets.',
    queryParams: [
      { name: 'category', type: 'string', description: 'Data category filter', example: 'defi', required: false },
      { name: 'limit', type: 'integer', description: 'Number of results to return', example: 10, required: false },
    ],
  },
  '/v1/airdrops/check': {
    method: 'post',
    summary: 'Check wallet for airdrop eligibility',
    description: 'Check if a wallet address is eligible for any tracked airdrops. Returns eligibility status, claimable amounts, and deadlines.',
    requestBody: {
      required: true,
      properties: [
        { name: 'address', type: 'string', description: 'Wallet address to check (EVM or Solana)', example: '0x7EBff1DbD34172C5b55697654006C9642b5236a3' },
        { name: 'chain', type: 'string', description: 'Blockchain to check (ethereum, solana, base)', example: 'base' },
      ],
    },
  },
  '/v1/wallet/analyze': {
    method: 'post',
    summary: 'Analyze a wallet portfolio',
    description: 'Analyze a wallet address for token holdings, portfolio value, risk score, and trading activity. Returns comprehensive analytics.',
    requestBody: {
      required: true,
      properties: [
        { name: 'address', type: 'string', description: 'Wallet address to analyze', example: '0x7EBff1DbD34172C5b55697654006C9642b5236a3' },
        { name: 'chain', type: 'string', description: 'Chain to analyze (ethereum, base, solana)', example: 'base' },
      ],
    },
  },
  '/v1/nft/search': {
    method: 'get',
    summary: 'Search NFTs by collection or trait',
    description: 'Search for NFTs across collections by name, collection address, or trait attributes. Returns floor prices and marketplace links.',
    queryParams: [
      { name: 'collection', type: 'string', description: 'Collection name or address', example: 'Bored Ape Yacht Club', required: true },
      { name: 'limit', type: 'integer', description: 'Max results to return', example: 20, required: false },
    ],
  },
  '/v1/score/{mint}': {
    method: 'get',
    summary: 'Get token security score',
    description: 'Get a detailed security risk score for a Solana token by its mint address. Analyzes liquidity, holders, mint authority, and known risk factors.',
    pathParams: [{ name: 'mint', type: 'string', description: 'Solana token mint address (base58)', example: 'So11111111111111111111111111111111111111112' }],
  },
  '/v1/agent/scan': {
    method: 'post',
    summary: 'Scan and evaluate AI agent',
    description: 'Scan and evaluate an AI agent by its wallet address or platform URL. Returns reputation score, transaction history, and risk assessment.',
    requestBody: {
      required: true,
      properties: [
        { name: 'address', type: 'string', description: 'Agent wallet address to scan', example: '0x742d35Cc6634C0532925a3b844Bc454e4438f44f' },
        { name: 'chain', type: 'string', description: 'Blockchain network', example: 'base' },
      ],
    },
  },
};
```

## Generator function (handleOpenAPI)

```typescript
function handleOpenAPI(): Response {
  const paths: any = {};

  for (const [route, price] of Object.entries(PRICING)) {
    const meta = getEndpointMeta(route);
    const method = meta.method || 'get';

    // Build parameters array
    const parameters: any[] = [];

    // Add path parameters
    if (meta.pathParams) {
      for (const p of meta.pathParams) {
        parameters.push({
          name: p.name,
          in: 'path',
          required: true,
          schema: { type: p.type },
          description: p.description,
          example: p.example,
        });
      }
    }

    // Add query parameters  
    if (meta.queryParams) {
      for (const p of meta.queryParams) {
        parameters.push({
          name: p.name,
          in: 'query',
          required: p.required || false,
          schema: { type: p.type },
          description: p.description,
          example: p.example,
        });
      }
    }

    // Build requestBody if applicable
    let requestBody: any = undefined;
    if (method === 'post' && meta.requestBody) {
      const properties: Record<string, any> = {};
      const required: string[] = [];
      for (const prop of meta.requestBody.properties) {
        properties[prop.name] = {
          type: prop.type,
          description: prop.description,
        };
        if (prop.required !== false) required.push(prop.name);
      }
      requestBody = {
        required: meta.requestBody.required ?? true,
        content: {
          'application/json': {
            schema: {
              type: 'object',
              ...(required.length > 0 ? { required } : {}),
              properties,
            },
            example: Object.fromEntries(
              meta.requestBody.properties.map(p => [p.name, p.example])
            ),
          },
        },
      };
    }

    // 402 response schema
    const paymentRequiredSchema = {
      type: 'object',
      properties: {
        status: { type: 'integer', example: 402 },
        title: { type: 'string', example: 'Payment Required' },
        detail: { type: 'string', example: `This endpoint costs $${price.toFixed(3)} USDC.` },
        x402version: { type: 'string', example: 'x402-v2' },
        accepts: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              type: { type: 'string', example: 'x402' },
              scheme: { type: 'string', example: 'exact' },
              network: { type: 'string', example: 'eip155:8453' },
              amount: { type: 'string', example: String(price * 1_000_000) },
              asset: { type: 'string', example: '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913' },
              payTo: { type: 'string', example: '0x7EBff1DbD34172C5b55697654006C9642b5236a3' },
              maxTimeoutSeconds: { type: 'integer', example: 60 },
            },
          },
        },
      },
    };

    const operation: any = {
      summary: meta.summary,
      description: `**x402 paid endpoint** — Cost: **$${price.toFixed(3)} USDC**.`,
      parameters,
      responses: {
        '200': {
          description: 'Successful response — data returned after payment verification',
          content: { 'application/json': { schema: { type: 'object' } } },
        },
        '402': {
          description: 'Payment required — includes x402 payment instructions',
          content: { 'application/json': { schema: paymentRequiredSchema } },
        },
      },
    };

    if (requestBody) {
      operation.requestBody = requestBody;
    }

    operation.security = [{ x402: [] }];
    paths[route] = { [method]: operation };
  }

  return jsonResponse({
    openapi: '3.0.0',
    info: {
      title: 'GenTech x402 Gateway',
      version: CONFIG.VERSION,
      description: 'API endpoints paid per-call via x402.',
    },
    servers: [
      { url: 'https://api.gentechlabs.net', description: 'Production' },
    ],
    security: [{ x402: [] }],
    components: {
      securitySchemes: {
        x402: {
          type: 'apiKey',
          in: 'header',
          name: 'X-Payment-Proof',
          description: 'x402 payment proof (base64-encoded JSON)',
        },
      },
    },
    externalDocs: {
      description: 'x402 Protocol Specification',
      url: 'https://x402.org',
    },
    paths,
  });
}
```

## Generated output verification

After deploying, verify the spec programmatically:

```bash
curl -s "https://api.gentechlabs.net/openapi.json" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Servers:', d.get('servers'))
print('Paths:', len(d.get('paths', {})))
print('Has components:', 'components' in d)
print('Has externalDocs:', 'externalDocs' in d)
print('Has security:', 'security' in d)

# Check a GET endpoint with path param
sc = d['paths']['/v1/score/{mint}']['get']
print('Score summary:', sc.get('summary'))
for p in sc.get('parameters', []):
    print(f'  Param: {p[\"name\"]} in={p[\"in\"]} example={p.get(\"example\",\"?\")}')

# Check a POST endpoint with requestBody
wa = d['paths']['/v1/wallet/analyze']
if 'post' in wa:
    p = wa['post']
    rb = p['requestBody']['content']['application/json']
    print('Wallet/analyze has schema:', 'schema' in rb)
    print('Wallet/analyze has example:', 'example' in rb)
"
```

Expected: all paths present, `components` includes `securitySchemes.x402`, each operation has `security: [{x402: []}]`, POST endpoints have `requestBody` with schema + example, and path params carry real examples.

## Pitfalls

- **Query param `required` matters** — Making a query param `required: true` causes the scanner to reject the endpoint. Always use `required: false` + default/example.
- **POST endpoint method detection** — If the OpenAPI spec says GET but the actual endpoint is POST, the scanner sends GET and gets 405 instead of 402. Match the metadata method to what the server actually handles.
- **Example values must be valid** — If the scanner uses your examples to construct requests, an invalid mint address or wallet address will fail probe. Use addresses that pass basic format validation (e.g. valid Solana base58 for `{mint}`, valid 0x hex for EVM addresses).
- **`info.x-payment-protocol` and `info.x-payment-token`** — These x- extensions are recommended for agent discovery. The `@agentcash/discovery` tool reports `INFO` level guidance when they're missing.
- **`favicon.ico`** — The scanner reports `FAVICON_MISSING` as a warning. This is cosmetic and does not block registration, but resolve it for a clean report.
