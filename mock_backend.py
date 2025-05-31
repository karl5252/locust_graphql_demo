import os
import random
import time

from flask import Flask, send_from_directory, request, jsonify

# )

app = Flask(__name__)


@app.route("/", methods=["POST"])
def graphql_handler():
    tenant = request.headers.get("X-Tenant-ID", "unknown")
    if tenant == "neverwinter":
        if random.random() < 0.3:
            return "Gamma crash", 500
        time.sleep(random.uniform(0.4, 1.2))
    elif tenant == "wonderland":
        time.sleep(random.uniform(0.2, 0.4))
    else:
        time.sleep(random.uniform(0.05, 0.1))
    return jsonify({"data": {"status": "ok", "tenant": tenant}})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
