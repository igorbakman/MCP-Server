def test_exchange_direct_pair(client):
    r = client.get("/exchange", params={"from": "USD", "to": "EUR", "amount": 10})
    assert r.status_code == 200
    body = r.json()
    assert body["converted"] == 9.0
    assert body["rate_used"] == 0.9


def test_exchange_cross_via_usd(client):
    r = client.get("/exchange", params={"from": "EUR", "to": "GBP", "amount": 10})
    assert r.status_code == 200
    body = r.json()
    expected = 0.8 / 0.9  # USD->GBP / USD->EUR
    assert round(body["rate_used"], 6) == round(expected, 6)
    assert body["via"]  # contains ["USD"] for crossed pairs


def test_exchange_invalid_currency(client):
    r = client.get("/exchange", params={"from": "AAA", "to": "EUR", "amount": 10})
    assert r.status_code == 400
