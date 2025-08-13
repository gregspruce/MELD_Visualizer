def test_root_responds(dash_app):
    server = dash_app.server
    client = server.test_client()
    resp = client.get("/")
    assert resp.status_code in (200, 302)

def test_layout_exists(dash_app):
    assert dash_app.layout is not None
