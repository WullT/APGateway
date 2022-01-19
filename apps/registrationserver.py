# https://fhnw.mit-license.org/

from flask import Flask, request, make_response, jsonify
import sqliteadapter

PORT = 8888

app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register():
    req = request.json
    if not req is None:
        if "hostname" in req:
            hostname = req["hostname"]
            if hostname is not None and len(hostname) > 4:
                sqliteadapter.add_new_camera(hostname)
                return make_response(jsonify(success=True), 200)
            return make_response(jsonify({"error": "hostname missing or too short"}), 400)
        return make_response(jsonify({"error": "hostname missing"}), 400)
    return make_response(jsonify({"error": "no json content"}), 400)

if "__main__" == __name__:
    app.run(host="0.0.0.0", port=PORT, debug=False)

