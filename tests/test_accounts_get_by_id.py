import uuid
from decimal import Decimal


def test_get_account_by_id(client, auth_header):
    # 1) Crear customer
    email = f"acct-{uuid.uuid4()}@finledger.com"
    r1 = client.post(
        "/customers",
        headers=auth_header,
        json={"name": "ACME SpA", "email": email},
    )
    assert r1.status_code in (200, 201), r1.text
    customer_id = r1.json()["id"]

    # 2) Crear account
    r2 = client.post(
        "/accounts",
        headers=auth_header,
        json={"customer_id": customer_id, "currency": "CLP"},
    )
    assert r2.status_code in (200, 201), r2.text
    account_id = r2.json()["id"]

    # 3) GET /accounts/{id}
    r3 = client.get(f"/accounts/{account_id}", headers=auth_header)
    assert r3.status_code == 200, r3.text
    data = r3.json()

    assert data["id"] == account_id
    assert data["customer_id"] == customer_id
    assert data["currency"] == "CLP"
    assert Decimal(data["balance"]) == Decimal("0.00")
    assert data["is_active"] is True
    assert "created_at" in data
