import math
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

UNITS = ("celsius", "fahrenheit", "kelvin")
ABSOLUTE_ZERO_C = -273.15


def to_celsius(value, unit):
    if unit == "fahrenheit":
        return (value - 32) * 5 / 9
    if unit == "kelvin":
        return value - 273.15
    return value


def from_celsius(value, unit):
    if unit == "fahrenheit":
        return value * 9 / 5 + 32
    if unit == "kelvin":
        return value + 273.15
    return value


def convert_temperature(value, from_unit, to_unit):
    """Convert between celsius, fahrenheit and kelvin via celsius."""
    celsius = to_celsius(value, from_unit)
    if celsius < ABSOLUTE_ZERO_C - 1e-9:
        raise ValueError("Temperature is below absolute zero")
    return from_celsius(celsius, to_unit)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Temperature Converter</title>
<style>
  :root {
    --bg: #0d1117; --panel: #161b22; --border: #30363d;
    --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff; --err: #f85149;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; min-height: 100vh; display: grid; place-items: center;
    background: radial-gradient(circle at 50% 30%, #1b2432, var(--bg) 60%);
    color: var(--text);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  main {
    width: min(92vw, 460px); background: var(--panel);
    border: 1px solid var(--border); border-radius: 12px; padding: 2rem;
  }
  h1 { margin: 0 0 .25rem; font-size: 1.4rem; }
  .sub { margin: 0 0 1.5rem; color: var(--muted); font-size: .9rem; }
  label { display: block; font-size: .8rem; color: var(--muted); margin-bottom: .35rem; }
  input, select {
    width: 100%; padding: .7rem .8rem; background: var(--bg); color: var(--text);
    border: 1px solid var(--border); border-radius: 8px; font-size: 1rem;
  }
  input:focus, select:focus, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
  .row { display: grid; grid-template-columns: 1fr auto 1fr; gap: .6rem; align-items: end; margin-top: 1rem; }
  button {
    padding: .7rem .9rem; background: transparent; color: var(--accent);
    border: 1px solid var(--border); border-radius: 8px; font-size: 1rem; cursor: pointer;
  }
  button:hover { border-color: var(--accent); }
  #result {
    margin-top: 1.5rem; padding: 1rem; min-height: 4rem; display: flex; align-items: center;
    background: var(--bg); border: 1px solid var(--border); border-radius: 8px;
    font-size: 1.6rem; font-weight: 600;
  }
  #result.error { color: var(--err); font-size: 1rem; font-weight: 400; }
  footer { margin-top: 1rem; color: var(--muted); font-size: .75rem; text-align: center; }
</style>
</head>
<body>
<main>
  <h1>Temperature Converter</h1>
  <p class="sub">Type a value and the result updates instantly.</p>

  <label for="value">Value</label>
  <input id="value" type="number" step="any" value="25" autofocus>

  <div class="row">
    <div>
      <label for="from">From</label>
      <select id="from">
        <option value="celsius" selected>Celsius</option>
        <option value="fahrenheit">Fahrenheit</option>
        <option value="kelvin">Kelvin</option>
      </select>
    </div>
    <button id="swap" type="button" aria-label="Swap units">&#8644;</button>
    <div>
      <label for="to">To</label>
      <select id="to">
        <option value="celsius">Celsius</option>
        <option value="fahrenheit" selected>Fahrenheit</option>
        <option value="kelvin">Kelvin</option>
      </select>
    </div>
  </div>

  <div id="result" aria-live="polite"></div>
  <footer>Temp Converter API - Dekasrepo</footer>
</main>
<script>
  const $ = (id) => document.getElementById(id);
  const symbols = { celsius: "\\u00b0C", fahrenheit: "\\u00b0F", kelvin: "K" };
  let timer;

  async function convert() {
    const value = $("value").value;
    const result = $("result");
    if (value === "") { result.className = ""; result.textContent = ""; return; }
    const params = new URLSearchParams({ value: value, from: $("from").value, to: $("to").value });
    try {
      const res = await fetch("/api/convert?" + params);
      const data = await res.json();
      if (!res.ok) { throw new Error(data.error || "Conversion failed"); }
      result.className = "";
      result.textContent = data.result + " " + symbols[data.to];
    } catch (err) {
      result.className = "error";
      result.textContent = err.message;
    }
  }

  function schedule() { clearTimeout(timer); timer = setTimeout(convert, 150); }

  $("value").addEventListener("input", schedule);
  $("from").addEventListener("change", convert);
  $("to").addEventListener("change", convert);
  $("swap").addEventListener("click", () => {
    const previous = $("from").value;
    $("from").value = $("to").value;
    $("to").value = previous;
    convert();
  });
  convert();
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return PAGE


@app.route("/health")
def health():
    return jsonify(status="ok", message="Temp Converter API - Dekasrepo"), 200


@app.route("/api/convert")
def api_convert():
    value = request.args.get("value", type=float)
    from_unit = request.args.get("from", "").lower()
    to_unit = request.args.get("to", "").lower()

    if value is None or not math.isfinite(value):
        return jsonify(error="'value' must be a finite number"), 400
    if from_unit not in UNITS or to_unit not in UNITS:
        return jsonify(error="'from' and 'to' must be one of: " + ", ".join(UNITS)), 400

    try:
        result = convert_temperature(value, from_unit, to_unit)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    return jsonify({"value": value, "from": from_unit, "to": to_unit, "result": round(result, 2)}), 200


# Kept so existing links and the original tests keep working.
@app.route("/convert")
def convert_legacy():
    celsius = request.args.get("celsius", type=float)
    if celsius is None or not math.isfinite(celsius):
        return jsonify(error="Provide a 'celsius' query param, e.g. /convert?celsius=25"), 400
    try:
        fahrenheit = convert_temperature(celsius, "celsius", "fahrenheit")
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(celsius=celsius, fahrenheit=fahrenheit), 200


if __name__ == "__main__":
    # Local development only. In the container, gunicorn serves the app (see Dockerfile).
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8080")))
    