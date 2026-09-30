from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def health():
    return jsonify(status="ok", message="Temp Converter API - Dekasrepo"), 200


@app.route("/convert")
def convert():
    celsius = request.args.get("celsius", type=float)
    if celsius is None:
        return jsonify(error="Provide a 'celsius' query param, e.g. /convert?celsius=25"), 400
    fahrenheit = (celsius * 9 / 5) + 32
    return jsonify(celsius=celsius, fahrenheit=fahrenheit), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
