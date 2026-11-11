# Threat model

Passage is a teaching demo. This file states what each party can and cannot learn, what
the tests pin down, and what is deliberately not protected.

## What the scheme is

At issuance the issuer picks a random salt and computes `commitment = SHA256(status || salt)`.
The commitment is signed (HMAC-SHA256) and `keccak256(credential_id : commitment)` is anchored
on `DidRegistry`. The holder keeps the salt. To present, the wallet sends
`proof = SHA256(claimed_status || salt)`; the verifier checks `proof == commitment` and
asks the chain whether the credential hash is anchored and not revoked.

This is a **salted hash commitment**, not a zero-knowledge proof.

## Who learns what

| Data | Issuer | Wallet | Customs | Chain |
|---|---|---|---|---|
| Name, passport, nationality | yes | yes | no | no |
| Blinding salt | at issuance only | yes | no | no |
| Status commitment | yes | yes | yes | only its keccak hash |
| Revocation state | yes | yes | yes | yes |
| That a given credential was presented | no | yes | yes | no |

Customs sees only `credential_id`, a status label and a hash. It cannot recover the salt or
any personal field from them.

## What an attacker can and cannot do

| Attack | Result | Test |
|---|---|---|
| Edit one character of the proof | Rejected | `test_tampered_proof_rejected` |
| Present a proof for a status you were not issued | Rejected | `test_proof_for_other_status_rejected` |
| Guess the salt | Rejected (128-bit random salt) | `test_wrong_salt_rejected` |
| Present a revoked credential with a valid proof | Rejected, read live from the chain | `test_revoked_credential_rejected_with_valid_proof` |
| Revoke or anchor from a non-controller account | Contract reverts | `test_contract_only_controller_can_anchor_and_revoke` |
| Double revoke | Contract reverts | `test_contract_double_revoke_reverts` |
| Brute-force the status from the commitment | Only 3 statuses, but each needs the salt | n/a |
| **Replay a captured proof** | **Accepted** | `test_replay_is_accepted_known_limitation` |
| **Present a VALID proof under another label** | **Accepted** | `test_label_not_bound_known_limitation` |
| Forge the issuer signature | Not checked at verification time (see below) | none |

## Known limitations (not fixed)

- **Replay.** The proof is static, so anyone who sees it (a shoulder-surfer, a logged QR) can
  reuse it until the credential expires or is revoked. Fixing this needs a verifier challenge
  bound into the proof, which a plain hash commitment cannot support. A real ZK or
  signature-based scheme (BBS+, SD-JWT with holder binding) can.
- **Label not bound.** The verifier cannot recompute `SHA256(claimed_status || salt)` without
  the salt, so `claimed_status` is only a label. Because the commitment encodes the *issued*
  status, a holder cannot upgrade DENIED to VALID, but a VALID holder can attach any label.
  Customs should treat the label as display text, not as the verified fact.
- **Symmetric signature.** HMAC means only the issuer backend can verify the signature, so the
  customs path ignores it and trusts the chain plus the commitment instead. A production system
  uses ECDSA or EdDSA so verifiers need only a public key.
- **No holder binding.** Nothing proves the person presenting the proof is the credential
  holder. Anyone with the proof and credential id can present it.
- **Demo-grade key and access handling.** One default signing secret, one chain account that
  controls every DID, no authentication on the consoles, JSON files for storage.
- **Linkability.** The same `credential_id` is shown on every presentation, so repeated
  presentations are linkable by customs.
- **Metadata.** Anchoring and revocation timestamps are public on-chain.

## Next steps if this were to grow

Replace the commitment with SD-JWT VC or BBS+, add a verifier nonce and holder key binding,
switch the signature to EdDSA, and move from Ganache to a public testnet.
