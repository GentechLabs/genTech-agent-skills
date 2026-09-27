# Verifying a ported mechanism runs — mocked backend, no API cost

When you port a mechanism from a reference repo (borrow-the-mechanism step 4:
"verify it actually runs"), you do NOT need to spend API tokens to prove the
core logic is sound. Mock the backend and unit-test the math before wiring real
credentials.

## Pattern (used Aug 23, 2026 on llm-as-a-verifier)

1. **Port the ~200-line core** into `10-Labs/<project>/<module>.py` — self-contained,
   independent of the upstream repo.
2. **Mock the LLM backend** so `.chat.completions.create()` returns fixed token
   logprobs without any network call. Assert the scoring math separates cases:
   - confident best → ~1.0
   - confident worst → ~0.0
   - regex/text fallback → expected normalized value
3. Only after the mocked math passes, wire a real key for an end-to-end smoke
   test (e.g. does it rank a *correct* candidate over a *wrong* one?).

## Mock shape that actually works (pitfall)

The fake client must mirror the real OpenAI client's **attribute chain**
`client.chat.completions.create(...)`, not a flat `.create()`:

```python
class FakeCompletions:
    def create(self, **kw): ...   # build FakeResp here
class FakeClient:
    def __init__(self):
        self.chat = type("Chat", (), {"completions": FakeCompletions(self)})()
```

Then monkeypatch the module's client factory to return your fake, and accept
`*a, **kw` on the fake factory so the positional `base_url/api_key` args don't
blow up:

```python
_orig = module._build_client
module._build_client = lambda *a, **kw: FakeClient("A", 0.95)  # confident A
```

## The real trap — tokenization alignment

When simulating the verifier's `<score_A>` tag, the tokenizer matcher lowercases
the tag to `["score_a"]` and reads the logprob distribution at the position
**immediately after** the matched tag token (`i+n`). If your fake emits `score_A`
(mixed case) or places the distribution at the wrong index, the logprob path is
silently skipped and the test reads the literal text fallback instead — which
can make a "confident T" case wrongly return ~1.0 (from the literal `A` in the
text). Align the fake tokens to what the matcher expects before trusting a pass.

## Verdict output

Write the tested result into the borrow spec (`09-Green Room/specs/<topic>-borrow.md`):
what was BORROWED (the mechanism, ported + tested), what was SPIT OUT (the tool
as a dependency), and the pass/fail of the mocked verification. Lead with the
verdict, not the architecture.
