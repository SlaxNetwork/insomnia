import atexit
import hashlib
import hmac
import os
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from deployment_queue import publish_queued_assets, queue_asset_for_publication

app = Flask(__name__)

# Implemented a queue because sometimes GitHub doesn't
# update its resources fast enough, gives it some time so we
# can properly fetch it.
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=publish_queued_assets,
    trigger="interval",
    seconds=15
)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


@app.route("/payload", methods=["POST"])
def payload():
    headers = request.headers

    # check for auth.
    if not verify_signature(request):
        return {"ok": False}

    # make sure we're only handling json data.
    content_type = headers.get("Content-Type", None)
    if content_type is None or content_type != "application/json":
        return {"ok": False}

    # only handle releases.
    event_type = headers.get("X-Github-Event", None)
    if event_type is None or event_type.lower() != "release":
        return {"ok": False}

    body = request.json

    # only add to queue if published.
    action = body['action']
    if action != "published":
        return {"ok": False}

    assets_url = body['release']['assets_url']
    queue_asset_for_publication(assets_url)

    return {"ok": True}


def verify_signature(request_data):
    signature = "sha256=" + hmac.new(
        bytes(os.environ["SECRET_KEY"], 'utf-8'),
        msg=request_data.data,
        digestmod=hashlib.sha256
    ).hexdigest().lower()
    return hmac.compare_digest(signature, request_data.headers['X-Hub-Signature-256'])


if __name__ == '__main__':
    app.run(debug=True)
