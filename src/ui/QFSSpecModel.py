from Qt.QtCore import Qt, QAbstractItemModel, QModelIndex
from Qt.QtWidgets import QFileIconProvider, QStyle, QApplication
from Qt.QtGui import QMovie, QIcon

from pathlib import Path, PosixPath
from fsspec import AbstractFileSystem
from typing import Union, Any, List
from fonticon_mdi7 import MDI7
from superqt.fonticon import icon


def file_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024**2:
        return f"{round(size / 1024, 2)} KB"
    elif size < 1024**3:
        return f"{round(size / 1024**2, 2)} MB"
    elif size < 1024**4:
        return f"{round(size / 1024**3, 2)} GB"
    else:
        return f"{round(size / 1024**4, 2)} TB"


class FSTreeItem:
    def __init__(self, fs: AbstractFileSystem, path: PosixPath, parent=None):
        try:
            self.fs = fs
            self._path = path
            self._children = None
            self.parent = parent
            # print(f"Path on init: {self.path}")
            self.info = fs.info(self.path)
            self.being_fetched = False
            self.is_cached = False
        except Exception as e:
            print(f"Error: {e}")

    @property
    def path(self):
        return str(self._path)

    @property
    def children(self):
        if self.is_file:
            return []

        if self._children is None:
            items = [PosixPath(p) for p in self.fs.ls(self.path)]
            items = [p for p in items if not p == self._path]
            items = sorted(items, key=lambda x: x.name)
            self._children = [FSTreeItem(self.fs, p, self) for p in items]

        return self._children

    @property
    def is_dir(self):
        return self.info["type"] == "directory"

    @property
    def is_file(self):
        return self.info["type"] == "file"

    @property
    def extension(self):
        if self.is_file:
            return self._path.suffix
        else:
            return None

    def child(self, row):
        if self.children:
            return self.children[row]
        else:
            return None

    def childCount(self):
        return len(self.children)

    def childIndex(self):
        if self.parent is not None:
            return self.parent.children.index(self)

    def data(self, column):
        if column == 0:
            return self._path.name
        elif column == 1:
            if self.is_file:
                return file_size(self.info["size"])
            else:
                return None

    def columnCount(self):
        return 2


class QFSSpecModel(QAbstractItemModel):
    def __init__(
        self,
        fs: AbstractFileSystem,
        root_path: Union[str, PosixPath],
        openable_types: List[str],
        parent=None,
    ):
        super().__init__(parent)
        self._root = FSTreeItem(fs, PosixPath(root_path))
        self._openable_types = openable_types

        self._icon_provider = QFileIconProvider()
        self._loading_icon = icon(
            MDI7.download,
            color="white",
        )
        # print(self._loading_icon.actualSize())

    def index(
        self, row: int, column: int, parent=QModelIndex()
    ) -> Union[QModelIndex, None]:
        if not self.hasIndex(row, column, parent):
            return None

        if not parent.isValid():
            parentItem = self._root
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return None

    def parent(self, index: QModelIndex) -> Union[QModelIndex, None]:
        if not index.isValid():
            return None

        childItem = index.internalPointer()
        parentItem = childItem.parent

        if parentItem != self._root:
            return self.createIndex(parentItem.childIndex(), 0, parentItem)
        else:
            return QModelIndex()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not parent.isValid():
            parentItem = self._root
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return self._root.columnCount()

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == 0:
            return item.data(index.column())

        if role == 1 and index.column() == 0:
            if item.is_dir:
                return self._icon_provider.icon(QFileIconProvider.IconType.Folder)
            elif item.is_file:
                if item.being_fetched:
                    app = QApplication.instance()

                    icon = app.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
                    return icon
                elif item.is_cached:
                    app = QApplication.instance()

                    icon = app.style().standardIcon(
                        QStyle.StandardPixmap.SP_DialogApplyButton
                    )
                    return icon
                else:
                    return self._icon_provider.icon(QFileIconProvider.IconType.File)
        else:
            return None

    def hasChildren(self, parent: QModelIndex = ...) -> bool:
        if not parent.isValid():
            parentItem = self._root
        else:
            parentItem = parent.internalPointer()

        return parentItem.is_dir

    def headerData(self, section, orientation, role=...):
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            if section == 0:
                return "Name"
            elif section == 1:
                return "Size"

    def flags(self, index: QModelIndex) -> Union[Qt.ItemFlag, None]:
        if not index.isValid():
            return None

        item = index.internalPointer()

        if item.is_dir:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        if item.is_file:
            if item.extension in self._openable_types:
                return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            else:
                return Qt.ItemFlag.ItemIsSelectable
