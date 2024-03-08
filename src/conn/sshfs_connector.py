import functools

import chimerax.core.settings
from asyncssh import SSHClient
from asyncssh.auth import KbdIntPrompts, KbdIntResponse
from asyncssh.misc import MaybeAwait
from asyncio import sleep
import sshfs
from fsspec.asyn import get_running_loop, sync_wrapper, sync
from functools import partial
from superqt import ensure_main_thread, ensure_object_thread
import asyncio

from typing import Optional, List, Any
import concurrent.futures
import qasync

# from time import sleep

from .connector import Connector
from ..ui.sshfs_widgets import SSHFSDialog, SSHFSInput


class SimpleClient(SSHClient):

    def __init__(self, kbdint_responses: List[str]):
        super().__init__()
        self.kbdint_responses = kbdint_responses

    def kbdint_auth_requested(self) -> Optional[str]:
        print("kbdint_auth_requested")
        return ""

    async def kbdint_challenge_received(
        self, name: str, instructions: str, lang: str, prompts: KbdIntPrompts
    ) -> MaybeAwait[Optional[KbdIntResponse]]:
        print("kbdint_challenge_received")
        print(name, instructions, lang, prompts)
        if prompts:
            result = self.kbdint_responses
            return result
        else:
            return []


class SSHFSConnector(Connector):
    FS_TYPE = "sshfs"

    def __init__(
        self,
        preferred_host: str = "",
        preferred_user: str = "",
        preferred_port: int = 22,
        preferred_root: str = "",
    ):
        super().__init__()
        self.input_widget = SSHFSInput(
            preferred_user, preferred_host, preferred_port, preferred_root
        )

    def create_client(self, kbint_responses: List[str]):
        return SimpleClient(kbint_responses)

    def get_input(self) -> tuple[str, str, int, str, str, List[str]]:
        user = self.input_widget.user
        hostname = self.input_widget.host
        port = self.input_widget.port
        root = self.input_widget.root
        password = self.input_widget.password
        kbint_responses = self.input_widget.kbint_responses

        self.input_widget.clear()

        if not user:
            user = None
        if not port:
            port = 22

        return user, hostname, port, root, password, kbint_responses

    def connect(self):
        user, host, port, root, pw, kb = self.get_input()

        print(f"Connecting to {user}@{host}:{port}")

        fs = None
        try:
            fs = sshfs.SSHFileSystem(
                host,
                client_factory=functools.partial(self.create_client, kb),
                username=user,
                port=port,
                password=pw,
                preferred_auth=["password", "kbdint_auth"],
            )
        except Exception as e:
            print(f"Error: {e}")
            return None, None

        return fs, root
