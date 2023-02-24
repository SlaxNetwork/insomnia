import time
from handle_asset import prepare_asset_for_publication


class AssetQueueEntry:
    asset_url: str

    creation_time: float

    def __init__(self, asset_url: str):
        self.asset_url = asset_url
        self.creation_time = time.time()

    def publish(self):
        prepare_asset_for_publication(self.asset_url)


queue: list[AssetQueueEntry] = []
WAIT_TIME = 15.0  # in seconds.


def publish_queued_assets():
    if len(queue) > 0:
        print(f"Queued {len(queue)} entries.")

    for index, asset in enumerate(queue):
        # print(index, asset)
        creation_time = asset.creation_time

        diff = time.time() - creation_time
        # publish
        if diff > WAIT_TIME:
            try:
                asset.publish()
            except Exception as err:
                # well something went wrong.
                raise err
            finally:
                queue.pop(index)


def queue_asset_for_publication(asset_url: str):
    print("New asset placed in queue.")
    queue.append(AssetQueueEntry(asset_url))
