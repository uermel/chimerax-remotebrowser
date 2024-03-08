from typing import Optional

from Qt.QtCore import QObject
from Qt.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
)


class S3FSInput(QWidget):

    def __init__(
        self,
        preferred_profile: str = "",
        preferred_root: str = "",
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self._build(
            profile=preferred_profile,
            root=preferred_root,
        )

    @property
    def profile(self):
        return self._edit_profile.text()

    @property
    def root(self):
        return self._edit_root.text()

    def _build(self, profile: str = "", root: str = "/"):
        # Top level layout
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._upper = QHBoxLayout()
        self._middle = QHBoxLayout()
        self._lower = QHBoxLayout()

        # Labels
        self._label_profile = QLabel("Profile:")
        self._label_root = QLabel("Root:")

        self._edit_profile = QLineEdit(profile)
        self._edit_root = QLineEdit(root)

        self._upper.addStretch()
        self._upper.addWidget(self._label_profile)
        self._upper.addWidget(self._edit_profile)
        self._upper.addStretch()

        self._middle.addStretch()
        self._middle.addWidget(self._label_root)
        self._middle.addWidget(self._edit_root)
        self._middle.addStretch()

        self._layout.addLayout(self._upper)
        self._layout.addLayout(self._middle)

        self.setLayout(self._layout)
