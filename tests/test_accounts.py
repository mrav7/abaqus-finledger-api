import uuid
from fastapi.testclient import TestClient


def test_create_get_list_accounts(client: TestClient, auth_header):
    # Crear customer (necesario para accounts)
    email = f"acme-{uuid.uuid4()}@finledger.com"
    r = client.post("/customers", json={"name": "ACME SpA", "email": email}, headers=auth_header)
    assert r.status_code == 201, r.text
    customer_id = r.json()["id"]

    # Crear cuenta
    r2 = client.post("/accounts", json={"customer_id": customer_id, "currency": "CLP"}, headers=auth_header)
    assert r2.status_code == 201, r2.text
    acc = r2.json()
    assert acc["customer_id"] == customer_id
    assert acc["currency"] == "CLP"

    # Balance
    assert str(acc["balance"]) in ("0.00", "0", "0.0")

    # Get cuenta
    acc_id = acc["id"]
    r3 = client.get(f"/accounts/{acc_id}", headers=auth_header)
    assert r3.status_code == 200, r3.text
    assert r3.json()["id"] == acc_id

    # List por customer
    r4 = client.get(f"/customers/{customer_id}/accounts", headers=auth_header)
    assert r4.status_code == 200, r4.text
    data = r4.json()
    assert isinstance(data, list)
    assert any(a["id"] == acc_id for a in data)