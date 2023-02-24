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


# TODO: fix this entire task being blocked by the thread.
def publish_to_minio(name: str, jar_bytes: any, size: int):
    """
    Publish the downloaded jar to the MinIO instance,
    so it can be used to build servers for future deployments.
    :param name: jar name.
    :param jar_bytes: Bytes that make up an entire jar.
    :param size: size of the file.
    """

    try:
        # todo: use repo name
        deployment = load_deployment_information(name)
    except Exception as err:
        raise err

    if deployment is None:
        print("No deployment strategy found.", flush=True)
        return

    if "common" in deployment and deployment["common"]:
        deploy_common(name, jar_bytes, size)
    elif "servers" in deployment and len(deployment["servers"]) > 0:
        deploy_servers(name, jar_bytes, size, deployment["servers"])
    else:
        print("No deployment strategy found.", flush=True)


def deploy_common(name: str, jar_bytes: any, size: int):
    # create bucket
    if not client.bucket_exists("server-common"):
        client.make_bucket("server-common")

    res = client.put_object(
        "server-common",
        f"plugins/{name}",
        jar_bytes,
        length=size
    )
    print(f"Placed {name} at {res.location}")


def deploy_servers(name: str, jar_bytes: any, size: int, servers: list[str]):
    # create buckets
    for server in servers:
        server_bucket_name = f"server-{server}"

        if not client.bucket_exists(server_bucket_name):
            client.make_bucket(server_bucket_name)
            print(f"Creating bucket {server_bucket_name}.")

        res = client.put_object(
            server_bucket_name,
            f"plugins/{name}",
            jar_bytes,
            length=size
        )
        print(f"Placed {name} at {res.location}")


def load_deployment_information(name: str) -> any:
    with open("deployments.json", "r") as f:
        deployments_json = json.load(f)
        f.close()

    if name not in deployments_json:
        return None

    return deployments_json[name]