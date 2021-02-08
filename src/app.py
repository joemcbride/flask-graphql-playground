from flask import Flask, render_template, request, jsonify
from _graphql import execute
from schema import schema

app = Flask(__name__)


@app.route("/api/playground")
def playground():
    return render_template("playground.html", endpoint="/api/graphql")


@app.route("/api/graphql", methods=["POST"])
def graphql():
    data = request.get_json()
    return jsonify(execute(data, schema))


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
