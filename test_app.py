import pytest

from app import app, convert_temperature


@pytest.fixture
def client():
    return app.test_client()


def test_home_serves_the_ui(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Temperature Converter" in response.data


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


@pytest.mark.parametrize(
    "value, from_unit, to_unit, expected",
    [
        (0, "celsius", "fahrenheit", 32),
        (100, "celsius", "fahrenheit", 212),
        (212, "fahrenheit", "celsius", 100),
        (0, "celsius", "kelvin", 273.15),
        (0, "kelvin", "celsius", -273.15),
        (-459.67, "fahrenheit", "kelvin", 0),
        (25, "celsius", "celsius", 25),
    ],
)
def test_convert_temperature(value, from_unit, to_unit, expected):
    assert convert_temperature(value, from_unit, to_unit) == pytest.approx(expected)


def test_below_absolute_zero_raises():
    with pytest.raises(ValueError):
        convert_temperature(-300, "celsius", "kelvin")


def test_api_convert_ok(client):
    response = client.get("/api/convert?value=100&from=celsius&to=fahrenheit")
    assert response.status_code == 200
    assert response.get_json()["result"] == 212.0


def test_api_convert_accepts_mixed_case_units(client):
    response = client.get("/api/convert?value=0&from=Celsius&to=KELVIN")
    assert response.status_code == 200
    assert response.get_json()["result"] == 273.15


@pytest.mark.parametrize(
    "query",
    [
        "from=celsius&to=kelvin",                  # missing value
        "value=abc&from=celsius&to=kelvin",        # not a number
        "value=nan&from=celsius&to=kelvin",        # not finite
        "value=10&from=rankine&to=kelvin",         # unknown unit
        "value=10&from=celsius",                   # missing target unit
        "value=-300&from=celsius&to=kelvin",       # below absolute zero
    ],
)
def test_api_convert_rejects_bad_input(client, query):
    response = client.get("/api/convert?" + query)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_legacy_convert(client):
    response = client.get("/convert?celsius=0")
    assert response.status_code == 200
    assert response.get_json()["fahrenheit"] == 32.0


def test_legacy_convert_missing_param(client):
    response = client.get("/convert")
    assert response.status_code == 400
