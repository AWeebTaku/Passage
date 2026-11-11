"""Shared fixtures. Chain-backed tests need `python main.py` (or Ganache + deploy.py) running; they skip otherwise."""
import os
import sys
import uuid

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from backend import chain, storage  # noqa: E402
from backend.main import app  # noqa: E402


def _chain_ready() -> bool:
    try:
        return chain.get_w3().is_connected() and chain.did_exists("did:ssi:probe") is not None
    except Exception:
        return False


@pytest.fixture(scope="session")
def live_chain():
    if not _chain_ready():
        pytest.skip("Ganache + deployed DidRegistry not reachable (run `python main.py` first)")


@pytest.fixture
def client(live_chain, tmp_path, monkeypatch):
    """TestClient with throwaway storage so tests never touch your real wallets/registry."""
    for name in ("WALLET_FILE", "REGISTRY_FILE", "HOLDER_FILE"):
        monkeypatch.setattr(storage, name, str(tmp_path / f"{name.lower()}.json"))
    monkeypatch.setattr(storage, "STORAGE_DIR", str(tmp_path))
    with TestClient(app) as c:
        yield c


@pytest.fixture
def issued(client):
    """Issue one VALID credential; returns (credential_id, salt, holder_did)."""
    did = f"did:ssi:holder:test-{uuid.uuid4().hex[:8]}"
    r = client.post("/issue-visa", data=dict(holder_did=did, traveler_name="Test Traveler",
                                             passport_number="T1234567", nationality="IN"))
    assert r.status_code == 200, r.text
    cid = r.json()["credential_id"]
    salt = storage.read_wallets()[did][0]["salt"]
    return cid, salt, did
