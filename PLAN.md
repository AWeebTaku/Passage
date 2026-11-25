# Passage: plan

Reference: `../career-job-search-and-project-priorities.md` (priorities), `../career-role-market-research.md` (market evidence), `../profile-resume.md` and `../profile-portfolio.md` (how to present it).

## Brief

**Status:** built. **One line:** Selective-disclosure credential demo with an on-chain revocation registry.

**Roles it serves:** Backend (lead); full-stack (support)

**Stack:** FastAPI, Solidity, Web3.py, Jinja2, Tailwind

**Resume and portfolio line (truthful, edit numbers only if they change):**
- Signed hash commitments, on-chain revocation, verifier never sees raw personal data. Not a zero-knowledge protocol; say so.

**Proof gaps (what a reviewer will look for):**
- Only 2 tests; no CI; no threat model; no live demo.

**Next (only this):**
Tests, CI, threat model, hosted demo.

## Suggestions and status log

Priority: **High** (rare, impressive topic). Biggest gap: tests and honesty about the crypto.

1. Be explicit in README: current scheme is HMAC + SHA-256 commitments, **not** a real ZKP. Either rename ("selective disclosure demo") or add a real proof (e.g. Merkle-tree selective disclosure, or BBS+/SD-JWT) as v2.
2. Tests: only `tests/test_app.py` exists. Add contract tests (revoke/verify) and backend tests for tampered proofs, replayed proofs, revoked credentials.
3. Threat model doc: what issuer/holder/verifier can and cannot learn.
4. One-command setup (Ganache + deploy + run); remove `node_modules` and `build/` from the repo, add `.gitignore`.
5. Hosted demo or a screen recording of issue -> present -> revoke.
6. Align with W3C VC/DID formats where cheap (JSON-LD credential shape).

Later: replace Ganache with a testnet, wallet in browser with WebCrypto only.

### Status update (2026-11-11) and new priority

Priority: **finish quickly, then pause.**

Done: `.gitignore`, README says it is not a real zero-knowledge protocol, UI redesign and landing page, new `backend/vc.py` and `pytest.ini`.
Left:
- [x] Commit the pending work (committed in e4d076e).
- [x] Tests: 18 now (tampered, replayed, revoked, contract), see `tests/test_flow.py`.
- [x] Threat-model section in the README, plus `THREAT_MODEL.md`.
- [x] CI workflow: `.github/workflows/ci.yml` (Ganache, deploy, pytest, stale-Pages check). Not yet run on GitHub.
- [x] `build/` is gitignored (only `.gitkeep` tracked).

### Role-focus update (2026-11-25)

**Roles:** Backend (lead for crypto/API work), full-stack (support). **Priority: finish quickly, then show it.**
- [x] Tests and CI (see above).
- [ ] (Files ready, needs your Render account: `Dockerfile`, `render.yaml`, demo banner; Docker build untested here) A **live demo** is what turns this into a full-stack deployed project: run the backend on Render and replace local Ganache with an embedded chain or a public testnet for the demo (document which).
- [x] Threat-model section in the README; say "hash commitments", never "zero-knowledge", on the resume and portfolio.
- [x] One screenshot per role page (`docs/screenshots/`, still to add to the portfolio card) (issuer, wallet, customs) on the portfolio card.
