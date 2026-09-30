from app import app


def test_health():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_convert():
    client = app.test_client()
    response = client.get("/convert?celsius=0")
    assert response.status_code == 200
    assert response.get_json()["fahrenheit"] == 32.0


def test_convert_missing_param():
    client = app.test_client()
    response = client.get("/convert")
    assert response.status_code == 400
