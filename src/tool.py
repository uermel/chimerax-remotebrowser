# General
import os.path
from sys import platform

# ChimeraX
from chimerax.core.tools import ToolInstance
from chimerax.ui import MainToolWindow

# Qt
from Qt.QtGui import QFont
from Qt.QtWidgets import (
    QVBoxLayout,
)

from .conn.s3fs_connector import S3FSConnector
from .misc.env import env_if_mac
from .misc.settings import RemoteBrowserSettings
from .misc.util import openable_suffixes

# This tool
from .ui.main_widget import MainWidget
from .ui.QFSSpecModel import FSTreeItem

FSTYPES = {
    "s3fs": S3FSConnector,
    #    "sshfs": SSHFSConnector,
}


class RemoteBrowserTool(ToolInstance):
    # Does this instance persist when session closes
    SESSION_ENDURING = False
    # We do save/restore in sessions
    SESSION_SAVE = False
    # Let ChimeraX know about our help page
    # help = "help:user/tools/artiax.html"

    # ==============================================================================
    # Instance Initialization ======================================================
    # ==============================================================================

    def __init__(self, session, tool_name):
        # 'session'     - chimerax.core.session.Session instance
        # 'tool_name'   - string

        # Initialize base class
        super().__init__(session, tool_name)

        # Display Name
        self.display_name = "RemoteBrowser"

        # Store self in session
        session.remote_browser = self

        # Set the font
        if platform == "darwin":
            self.font = QFont("Arial", 10)
        else:
            self.font = QFont("Arial", 7)

        self.settings = RemoteBrowserSettings(session, "RemoteBrowser", version="1")
        """Default values for different file systems."""
        self.fstypes = {k: clz(**getattr(self.settings, k)) for k, clz in FSTYPES.items()}
        """The available remote file system types."""

        # UI
        self.tool_window = MainToolWindow(self, close_destroys=False)
        self._build_ui()

        # Zarr plugin available?
        self.can_read_omezarr = False
        try:
            self.can_read_omezarr = True
        except Exception:
            self.can_read_omezarr = False

        # If on MAC, add the zsh profile to the path (for AWS authentication)
        env_if_mac()

    def _build_ui(self):
        tw = self.tool_window

        self._layout = QVBoxLayout()
        self._mw = MainWidget(self.fstypes, openable_suffixes=openable_suffixes(self.session))
        self._layout.addWidget(self._mw)

        tw.ui_area.setLayout(self._layout)
        tw.manage("left")

        self._mw.file_caching_finished.connect(self.open_file)
        self._mw.openable_directory_clicked.connect(self.open_dir)

    def open_file(self, path: str):
        from chimerax.core.commands import run

        run(self.session, f"open {path}")

    def open_dir(self, item: FSTreeItem):
        if self.can_read_omezarr and os.path.splitext(item.path)[1] == ".zarr":
            from chimerax.ome_zarr.open import open_ome_zarr_from_fs

            models, msg = open_ome_zarr_from_fs(self.session, item.fs, item.path, initial_step=(4, 4, 4))

            self.session.models.add(models)
