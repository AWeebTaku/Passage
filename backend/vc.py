"""Export a wallet credential in the W3C Verifiable Credentials 2.0 data model shape.

Cheap alignment only. Two honest gaps:
- `did:ssi:*` is not a registered DID method.
- The proof is the issuer's HMAC-SHA256 (symmetric), so it is NOT a Data Integrity or
  JWS proof and a third party cannot verify it without the issuer secret.
The blinding salt is deliberately left out: it is a presentation secret, not credential data.
"""

VOCAB = "https://passage.invalid/vocab#"  # placeholder vocabulary; no such site exists


def to_vc(c: dict) -> dict:
    return {
        "@context": ["https://www.w3.org/ns/credentials/v2", {"@vocab": VOCAB}],
        "id": f"urn:passage:{c['credential_id']}",
        "type": ["VerifiableCredential", "TravelVisaCredential"],
        "issuer": c["issuer_did"],
        "validFrom": c["issued_at"],
        "validUntil": c["expiry_at"],
        "credentialSubject": {
            "id": c["holder_did"],
            "name": c["traveler_name"],
            "passportNumber": c["passport_number"],
            "nationality": c["nationality"],
            "visaStatus": c["visa_status"],
            "statusCommitment": c["commitment"],
        },
        "proof": {
            "type": "HmacSha256Proof",  # non-standard, see module docstring
            "created": c["issued_at"],
            "verificationMethod": f"{c['issuer_did']}#key-1",
            "proofPurpose": "assertionMethod",
            "proofValue": c["signature"],
        },
    }
