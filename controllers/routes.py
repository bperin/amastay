from flask import app, jsonify


@app.route("/routes", methods=["GET"])
def list_routes():
    import urllib

    output = []
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(rule.methods))
        url = urllib.parse.unquote(str(rule))
        output.append(f"{rule.endpoint}: {methods} {url}")
    return jsonify(output)
