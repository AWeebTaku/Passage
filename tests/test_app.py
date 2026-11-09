"""Run: python -m pytest tests  (or python tests/test_app.py). Validation fires before any chain call."""
from fastapi.testclient import TestClient
from backend.main import app, _is_expired

c = TestClient(app)
OK = dict(holder_did="did:ssi:holder:t", traveler_name="A", passport_number="X1", nationality="IN")


def test_validation():
    assert c.post("/issue-visa", data={**OK, "validity_days": 0}).status_code == 422
    assert c.post("/issue-visa", data={**OK, "validity_days": 9999}).status_code == 422
    assert c.post("/issue-visa", data={**OK, "visa_status": "BOGUS"}).status_code == 422
    assert c.post("/issue-visa", data={**OK, "holder_did": "nope"}).status_code == 422


def test_expiry_and_pages():
    assert _is_expired("2000-01-01T00:00:00Z") and not _is_expired("2999-01-01T00:00:00Z")
    for path in ("/", "/issuer", "/wallet", "/customs"):
        r = c.get(path)
        assert r.status_code == 200 and "—" not in r.text, path


if __name__ == "__main__":
    test_validation(); test_expiry_and_pages(); print("ok")
