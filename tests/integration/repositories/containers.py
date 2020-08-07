import contextlib
import time
import typing

import docker


@contextlib.contextmanager
def container(image_name: str) -> typing.Iterator[str]:
    client = docker.from_env()
    container = client.containers.run(image_name, detach=True)
    try:
        for _ in range(10):
            ip_address = container.attrs["NetworkSettings"]["IPAddress"]
            if ip_address:
                break
            time.sleep(0.1)
            container.reload()
        else:
            RuntimeError(f"Cannot create {image_name} container")

        yield ip_address
    finally:
        container.stop()
        container.remove()
