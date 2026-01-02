def test_network_connections_endpoint(client):
    res = client.get("/api/network/connections", params={"require_running": "false"})
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "ts" in data
    assert "engine_running" in data
