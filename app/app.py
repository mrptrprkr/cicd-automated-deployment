import os
import secrets
import platform
import socket
import time

import psutil
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

START_TIME = time.time()


def deployment_info():
    return {
        "environment": os.getenv("APP_ENV", "development"),
        "version": os.getenv("APP_VERSION", "dev"),
        "build_number": os.getenv("BUILD_NUMBER", "local"),
        "git_commit": os.getenv("GIT_COMMIT", "local"),
        "deployed_by": os.getenv("DEPLOYED_BY", "manual"),
    }


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(
        status="healthy",
        service="cicd-automated-deployment"
    )


@app.route("/ready")
def ready():
    return jsonify(
        status="ready",
        service="cicd-automated-deployment"
    )


@app.route("/api/status")
def status():
    return jsonify(
        service="cicd-automated-deployment",
        status="running",
        deployment=deployment_info()
    )


@app.route("/api/system")
def system():
    process = psutil.Process()

    return jsonify(
        hostname=socket.gethostname(),
        platform=platform.system(),
        python_version=platform.python_version(),
        cpu_cores=os.cpu_count(),
        memory_used_mb=round(process.memory_info().rss / 1024 / 1024, 2),
        uptime_seconds=round(time.time() - START_TIME, 2)
    )


@app.route("/api/secure")
def secure():
    expected_token = os.getenv("DASHBOARD_API_TOKEN")
    supplied_token = request.headers.get("X-API-Key", "")

    if not expected_token or not secrets.compare_digest(supplied_token, expected_token):
        return jsonify(error="unauthorized"), 401

    return jsonify(
        status="authorized",
        message="CI/CD secret injection verified"
    )


@app.route("/version")
def version():
    return jsonify(deployment_info())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
