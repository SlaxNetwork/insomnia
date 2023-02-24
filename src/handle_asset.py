import os
import requests
from publisher import publish_to_minio

GITHUB_KEY = os.environ["GITHUB_SECRET"]


def prepare_asset_for_publication(assets_url: str):
    """
    Find the jar asset and prepare it for MinIO publication.
    :param assets_url: All assets pertaining to a GitHub release.
    :return:
    """

    response = requests.get(
        assets_url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_KEY}"
        }
    )
    response.raise_for_status()

    assets = response.json()
    if len(assets) == 0:
        print("no assets found.")
        return

    jar_asset = get_jar_asset(assets)
    if jar_asset is None:
        print("no jar found.")

    jar_name = jar_asset['name']
    jar_size = jar_asset['size']

    print(f"Publishing {jar_name}")
    # get it to our minio inst.
    publish_to_minio(
        jar_name,
        get_raw_jar_binary(jar_asset),
        jar_size
    )


def get_raw_jar_binary(asset: any) -> any:
    """
    Download the bytes that make up a jar.
    :param asset: GitHub asset object.
    :return: Bytes
    """

    download_url = asset['url']

    response = requests.get(
        download_url,
        stream=True, headers={
            "Accept": "application/octet-stream",
            "Authorization": f"Bearer {GITHUB_KEY}"
        }
    )
    response.raise_for_status()

    return response.raw


def get_jar_asset(assets: any) -> any:
    for asset in assets:
        if asset['name'].endswith('.jar'):
            return asset
    return None
