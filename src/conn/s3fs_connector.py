import functools
import os

import aiobotocore
import s3fs
from fsspec.asyn import get_running_loop, sync_wrapper, sync
from functools import partial
from superqt import ensure_main_thread, ensure_object_thread
import asyncio

from typing import Optional, List, Any
import concurrent.futures
import qasync

# from time import sleep

from .connector import Connector
from ..ui.s3fs_widgets import S3FSInput


class S3FSConnector(Connector):
    FS_TYPE = "s3fs"

    def __init__(
        self,
        preferred_profile: str = "",
        preferred_root: str = "",
    ):
        super().__init__()
        self.input_widget = S3FSInput(preferred_profile, preferred_root)

    def get_input(self) -> tuple[str, str]:
        profile = self.input_widget.profile
        root = self.input_widget.root

        if not root:
            root = "/"

        return profile, root

    def connect(self):
        profile, root = self.get_input()

        fs = None
        try:
            if profile:
                print(f"Connecting to {root} using AWS profile {profile}")
                aiosess = aiobotocore.session.AioSession(profile=profile)
                fs = s3fs.S3FileSystem(session=aiosess)
            else:
                if "AWS_PROFILE" in os.environ:
                    print(f"Connecting to {root} using AWS profile {os.environ['AWS_PROFILE']}")
                    aiosess = aiobotocore.session.AioSession(profile=os.environ["AWS_PROFILE"])
                    fs = s3fs.S3FileSystem(session=aiosess)
                else:
                    print(f"Connecting to {root} anonymously")
                    fs = s3fs.S3FileSystem(anon=True)
        except Exception as e:
            print(f"Error: {e}")
            return None, None

        return fs, root
