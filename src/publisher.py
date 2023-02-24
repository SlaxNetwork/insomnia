import json
from minio import Minio
import os

client = Minio(
    os.environ["MINIO_HOST"],
    access_key=os.environ["MINIO_ACCESS_KEY"],
    secret_key=os.environ["MINIO_SECRET_KEY"],
    # secure=bool(os.environ["MINIO_SECURE"]),
    secure=False
)
print("SECURE ", bool(os.environ['MINIO_SECURE']))


class PluginDeployment:
    common: bool

    def __init__(self, common: bool):
        self.common = common


# TODO: fix this entire task being blocked by the thread.
def publish_to_minio(name: str, jar_bytes: any, size: int):
    """
    Publish the downloaded jar to the Google Cloud Storage instance,
    so it can be used to build servers for future deployments.
    :param name: jar name.
    :param jar_bytes: Bytes that make up an entire jar.
    :param size: size of the file.
    """

    if not client.bucket_exists("servers"):
        client.make_bucket("servers")
        print("servers bucket didn't exist, creating.")

    res = client.put_object(
        "servers",
        name,
        jar_bytes,
        length=size
    )
    print(f"Placed {name} at {res.location}")


# todo
def load_deployment_information(name: str) -> PluginDeployment:
    with open("deployments.json", "wb") as f:
        deployments_json = json.load(f)
        f.close()

    if name not in deployments_json:
        raise f"{name} is not a valid deployment."

    deployment_json = deployments_json[name]

    return PluginDeployment(
        bool(deployment_json['common'])
    )
