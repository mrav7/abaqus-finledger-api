import uuid
from decimal import Decimal


def test_smoke_e2e_flow(client, auth_header):
    # 1) customer
    email = f"smoke-{uuid.uuid4()}@finledger.com"
    r1 = client.post("/customers", headers=auth_header, json={"name": "Smoke SpA", "email": email})
    assert r1.status_code in (200, 201), r1.text
    customer_id = r1.json()["id"]

    # 2) account
    r2 = client.post("/accounts", headers=auth_header, json={"customer_id": customer_id, "currency": "CLP"})
    assert r2.status_code in (200, 201), r2.text
    account_id = r2.json()["id"]

    # 3) credit 100.00
    r3 = client.post(
        "/transactions",
        headers=auth_header,
        json={"account_id": account_id, "type": "credit", "amount": "100.00", "description": "topup"},
    )
    assert r3.status_code in (200, 201), r3.text

    # 4) debit 35.50
    r4 = client.post(
        "/transactions",
        headers=auth_header,
        json={"account_id": account_id, "type": "debit", "amount": "35.50", "description": "buy"},
    )
    assert r4.status_code in (200, 201), r4.text

    # 5) balance via GET /accounts/{id}
    r5 = client.get(f"/accounts/{account_id}", headers=auth_header)
    assert r5.status_code == 200, r5.text
    assert Decimal(r5.json()["balance"]) == Decimal("64.50")

    # 6) list tx
    r6 = client.get(f"/transactions?account_id={account_id}&limit=50&offset=0", headers=auth_header)
    assert r6.status_code == 200, r6.text
    data = r6.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
