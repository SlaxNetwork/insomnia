import atexit
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


if __name__ == '__main__':
    app.run()
