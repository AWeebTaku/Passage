"""Backend + contract behaviour. See THREAT_MODEL.md for why some tests pin known limitations."""
import hashlib
import uuid

import pytest
from web3.exceptions import ContractLogicError

from backend import chain, crypto_utils


def proof(status: str, salt: str) -> str:
    return hashlib.sha256(f"{status}{salt}".encode()).hexdigest()


def verify(client, cid, status, proof_hash):
    return client.post("/verify-border", data=dict(credential_id=cid, claimed_status=status, proof_hash=proof_hash)).json()


# ---- backend: what must be rejected -------------------------------------------------

def test_valid_proof_verifies(client, issued):
    cid, salt, _ = issued
    r = verify(client, cid, "VALID", proof("VALID", salt))
    assert r["verified"] and r["anchored"] and not r["revoked"]


def test_tampered_proof_rejected(client, issued):
    cid, salt, _ = issued
    good = proof("VALID", salt)
    bad = good[:-1] + ("0" if good[-1] != "0" else "1")
    r = verify(client, cid, "VALID", bad)
    assert not r["verified"] and not r["proof_valid"]


def test_proof_for_other_status_rejected(client, issued):
    """A holder issued VALID cannot present a proof computed for a status they were not issued."""
    cid, salt, _ = issued
    assert not verify(client, cid, "DENIED", proof("DENIED", salt))["verified"]


def test_wrong_salt_rejected(client, issued):
    cid, _, _ = issued
    assert not verify(client, cid, "VALID", proof("VALID", "guessed-salt"))["verified"]


def test_revoked_credential_rejected_with_valid_proof(client, issued):
    cid, salt, _ = issued
    assert client.post("/revoke-visa", data={"credential_id": cid}).status_code == 200
    r = verify(client, cid, "VALID", proof("VALID", salt))
    assert r["proof_valid"] and r["revoked"] and not r["verified"]


def test_unknown_credential_404(client):
    r = client.post("/verify-border", data=dict(credential_id="vc-nope", claimed_status="VALID", proof_hash="00"))
    assert r.status_code == 404


def test_duplicate_active_credential_conflict(client, issued):
    _, _, did = issued
    r = client.post("/issue-visa", data=dict(holder_did=did, traveler_name="x", passport_number="y", nationality="IN"))
    assert r.status_code == 409


def test_double_revoke_conflict(client, issued):
    cid, _, _ = issued
    assert client.post("/revoke-visa", data={"credential_id": cid}).status_code == 200
    assert client.post("/revoke-visa", data={"credential_id": cid}).status_code == 409


# ---- known limitations, pinned so a change is noticed (see THREAT_MODEL.md) ----------

def test_replay_is_accepted_known_limitation(client, issued):
    """No verifier nonce: the same proof verifies every time. Mitigation needs a challenge protocol."""
    cid, salt, _ = issued
    p = proof("VALID", salt)
    assert verify(client, cid, "VALID", p)["verified"]
    assert verify(client, cid, "VALID", p)["verified"]


def test_label_not_bound_known_limitation(client, issued):
    """The verifier compares proof to commitment only; claimed_status is a label it cannot check without the salt."""
    cid, salt, _ = issued
    assert verify(client, cid, "DENIED", proof("VALID", salt))["verified"]


# ---- contract -------------------------------------------------------------------------

@pytest.fixture
def issuer(client):
    did = f"did:ssi:issuer:test-{uuid.uuid4().hex[:8]}"
    chain.register_did(did, crypto_utils.generate_salt(32))
    return did


def h():
    return chain.credential_hash_bytes32(f"vc-{uuid.uuid4().hex}", "c0ffee")


def test_contract_anchor_then_revoke(client, issuer):
    ch = h()
    assert not chain.is_anchored(ch)
    chain.anchor_credential(issuer, ch)
    assert chain.is_anchored(ch) and not chain.is_revoked(ch)
    chain.revoke_credential(issuer, ch)
    assert chain.is_revoked(ch)
    assert chain.get_contract().functions.getRevocationTimestamp(ch).call() > 0


def test_contract_double_revoke_reverts(client, issuer):
    ch = h()
    chain.anchor_credential(issuer, ch)
    chain.revoke_credential(issuer, ch)
    with pytest.raises(ContractLogicError, match="already revoked"):
        chain.revoke_credential(issuer, ch)


def test_contract_only_controller_can_anchor_and_revoke(client, issuer):
    other = chain.get_w3().eth.accounts[1]
    assert other != chain.get_default_account()
    c = chain.get_contract().functions
    ch = h()
    with pytest.raises(ContractLogicError, match="not DID controller"):
        c.anchorCredential(issuer, ch).transact({"from": other})
    chain.anchor_credential(issuer, ch)
    with pytest.raises(ContractLogicError, match="not DID controller"):
        c.revokeCredential(issuer, ch).transact({"from": other})


def test_contract_unregistered_did_cannot_anchor(client):
    with pytest.raises(ContractLogicError, match="not registered"):
        chain.anchor_credential("did:ssi:issuer:ghost-" + uuid.uuid4().hex, h())


def test_contract_duplicate_did_reverts(client, issuer):
    with pytest.raises(ContractLogicError, match="already registered"):
        chain.register_did(issuer, "00")


# ---- W3C VC export --------------------------------------------------------------------

def test_vc_export_shape_and_no_salt(client, issued):
    cid, salt, did = issued
    r = client.get(f"/api/credential/{cid}/vc")
    assert r.status_code == 200 and r.headers["content-type"].startswith("application/vc+ld+json")
    doc = r.json()
    assert doc["@context"][0] == "https://www.w3.org/ns/credentials/v2"
    assert "VerifiableCredential" in doc["type"] and doc["credentialSubject"]["id"] == did
    assert salt not in r.text
    assert client.get("/api/credential/vc-nope/vc").status_code == 404
