from chimerax.core.settings import Settings


class RemoteBrowserSettings(Settings):
    AUTO_SAVE = {
        "sshfs": {
            "preferred_host": "127.0.0.1",
            "preferred_user": "",
            "preferred_port": 22,
            "preferred_root": "/",
        },
        "s3fs": {
            "preferred_profile": "",
            "preferred_root": "/",
        },
    }
