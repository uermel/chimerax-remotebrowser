# General
from functools import partial
from sys import platform
from qt_async_threads import QtAsyncRunner

# ChimeraX
from chimerax.core.tools import ToolInstance
from chimerax.ui import MainToolWindow
from chimerax.open_command.cmd import FileInfo, collated_open

# Qt
from Qt.QtCore import Qt
from Qt.QtGui import QFont, QKeySequence
from Qt.QtWidgets import (
    QAction,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QMenu,
    QMenuBar,
    QPushButton,
    QVBoxLayout,
    QSizePolicy,
)

# This tool
from .ui.main_widget import MainWidget
from .misc.settings import RemoteBrowserSettings
from .misc.util import openable_suffixes
from .conn.sshfs_connector import SSHFSConnector
from .conn.s3fs_connector import S3FSConnector

FSTYPES = {
    "sshfs": SSHFSConnector,
    "s3fs": S3FSConnector,
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
        self.fstypes = {
            k: clz(**getattr(self.settings, k)) for k, clz in FSTYPES.items()
        }
        """The available remote file system types."""

        # UI
        self.tool_window = MainToolWindow(self, close_destroys=False)
        self._build_ui()

    def _build_ui(self):
        tw = self.tool_window

        self._layout = QVBoxLayout()
        self._mw = MainWidget(
            self.fstypes, openable_suffixes=openable_suffixes(self.session)
        )
        self._layout.addWidget(self._mw)

        tw.ui_area.setLayout(self._layout)
        tw.manage("left")

        self._mw.file_caching_finished.connect(self.open_file)

    def open_file(self, path):
        from chimerax.core.commands import run

        run(self.session, f"open {path}")
