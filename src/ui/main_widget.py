import functools
from typing import Dict, Optional, List
from qt_async_threads import QtAsyncRunner
import os

from Qt.QtCore import Qt, QObject, QModelIndex, Signal
from Qt.QtGui import QFont, QKeySequence
from Qt.QtWidgets import (
    QWidget,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QSizePolicy,
    QComboBox,
    QTreeView,
    QLineEdit,
    QLabel,
    QStackedLayout,
)

from .util import QHLine
from ..misc.util import openable_suffixes
from ..conn.connector import Connector
from ..conn.sshfs_connector import SSHFSConnector
from .sshfs_widgets import SSHFSDialog
from .QFSSpecModel import QFSSpecModel, FSTreeItem
from fonticon_mdi7 import MDI7
from superqt.fonticon import icon


class MainWidget(QWidget):
    file_caching_finished = Signal(str)
    openable_directory_clicked = Signal(FSTreeItem)

    def __init__(
        self,
        fstypes: Dict[str, Connector],
        openable_suffixes: List[str] = None,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent=parent)
        self.fstypes = fstypes
        self.openable_suffixes = openable_suffixes

        self.runner = QtAsyncRunner()

        self.fs = None
        self.model = None

        self._build()
        self._connect()

    @property
    def connection_type(self):
        return self._type_combo.currentText()

    def _build(self):
        # Top level layout
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        # Conection box layout
        self._connectbox = QGroupBox("Connect")
        self._connectbox.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        )
        self._box_layout = QVBoxLayout()

        # Connection Button layout
        self._button_layout = QVBoxLayout()
        self._combo_layout = QHBoxLayout()

        # Connection Type combo box
        self._type_combo = QComboBox(parent=self._connectbox)
        self._type_combo.addItems(list(self.fstypes.keys()))

        # Connect/Disconnect buttons
        self._connect_button = QPushButton("Connect", parent=self._connectbox)
        self._disconnect_button = QPushButton("Disconnect", parent=self._connectbox)
        # self._disconnect_button.setEnabled(False)

        # self._connect_button.setIcon(icon(MDI7.download, color="white"))
        self._button_layout.addWidget(self._connect_button)
        self._button_layout.addWidget(self._disconnect_button)

        self._combo_layout.addWidget(self._type_combo)
        self._combo_layout.addLayout(self._button_layout)

        # Input layout
        self._input_layout = QStackedLayout()
        for fs in self.fstypes.values():
            self._input_layout.addWidget(fs.input_widget)

        self._input_layout.setCurrentIndex(0)

        # Connection Box layout
        self._box_layout.addLayout(self._combo_layout)
        self._box_layout.addLayout(self._input_layout)
        self._box_layout.addWidget(QHLine())
        self._connectbox.setLayout(self._box_layout)

        # Tree View
        self._tree_view = QTreeView(parent=self._connectbox)

        # Main layout
        self._layout.addWidget(self._connectbox)
        self._layout.addWidget(self._tree_view)

    def _connect(self):
        self._connect_button.clicked.connect(self._attempt_connection)
        self._disconnect_button.clicked.connect(self._disconnect)

        self._tree_view.expanded.connect(
            functools.partial(self._tree_view.resizeColumnToContents, 0)
        )
        self._tree_view.doubleClicked.connect(self.runner.to_sync(self._cache_file))

        self._type_combo.currentIndexChanged.connect(self._switch_fs)

    def _switch_fs(self, index: int):
        self._input_layout.setCurrentIndex(index)
        self._disconnect()

    def _disconnect(self):
        self._tree_view.setModel(None)

        if self.model:
            self.model.deleteLater()
            self.model = None

        if self.fs:
            del self.fs
            self.fs = None

    def _attempt_connection(self):
        # Remove old if any
        if self.model:
            self._disconnect()

        # try:
        fs, root = self.fstypes[self.connection_type].connect()
        print(f"Root: {root}")

        if fs:
            self.fs = fs
            self.model = QFSSpecModel(
                fs,
                root,
                self.openable_suffixes,
            )
            self._tree_view.setModel(self.model)
            self._tree_view.resizeColumnToContents(0)

    def readable_directory(self, name: str):
        ext = os.path.splitext(name)[1]
        if not ext:
            return

        if ext in self.openable_suffixes:
            return True
        else:
            return False

    async def _cache_file(self, index: QModelIndex):
        if not index.isValid():
            return

        item = index.internalPointer()

        if not item.is_file and not self.readable_directory(item.path):
            return

        if not item.is_file and self.readable_directory(item.path):
            self.openable_directory_clicked.emit(item)
            return

        target = "/tmp/" + item.path.lstrip("/")

        if item.is_cached and os.path.exists(target):
            print(f"File already cached at {target}")
            self._tree_view.model().dataChanged.emit(index, index)
            self.file_caching_finished.emit(target)
        else:
            print(f"Start Caching {item.path}")
            item.being_fetched = True
            self._tree_view.model().dataChanged.emit(index, index)

            os.makedirs(os.path.dirname(target), exist_ok=True)
            await self.runner.run(item.fs.get_file, *(item.path, target))

            item.being_fetched = False
            item.is_cached = True
            self._tree_view.model().dataChanged.emit(index, index)

            self.file_caching_finished.emit(target)
            print(f"Cached file to {target}")
