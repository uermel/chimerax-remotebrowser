from typing import Optional

from Qt.QtCore import Qt, QObject
from Qt.QtGui import QFont, QKeySequence
from Qt.QtWidgets import (
    QWidget,
    QAction,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QMenu,
    QMenuBar,
    QPushButton,
    QVBoxLayout,
    QSizePolicy,
    QLabel,
    QDialog,
    QTextEdit,
    QLineEdit,
)


class SSHFSDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SSH Server Prompt")
        self.setModal(False)

        self.prompt_text = ""
        self.response_echo = False
        self.response2 = None
        self._build()
        self._connect()

    def accept(self):
        self.response2 = self.response
        super().accept()

    def get_response(self):
        return self.response2

    @property
    def response(self):
        return self._response_edit.text()

    def _build(self):
        # Top level layout
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        # Server prompt output
        self._server_edit = QTextEdit()
        self._server_edit.setPlainText(self.prompt_text)
        self._server_edit.setReadOnly(True)

        # Response layout
        self._response_layout = QHBoxLayout()

        # Response input
        self._response_edit = QLineEdit()
        self._response_edit.setText("")
        if not self.response_echo:
            self._response_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self._send_button = QPushButton("Send")
        self._response_layout.addWidget(self._response_edit)
        self._response_layout.addWidget(self._send_button)

        # Cancel button
        self._cancel_button = QPushButton("Cancel")

        # Assemble
        self._layout.addWidget(self._server_edit)
        self._layout.addLayout(self._response_layout)
        self._layout.addWidget(self._cancel_button)

    def _connect(self):
        self._send_button.clicked.connect(self.accept)
        self._cancel_button.clicked.connect(self.reject)

    def set_prompt(self, prompts):
        self.prompt_text = prompts[0][0]
        self.response_echo = prompts[0][1]
        self._server_edit.setPlainText(self.prompt_text)
        if not self.response_echo:
            self._response_edit.setEchoMode(QLineEdit.EchoMode.Password)

    # def open(self, prompts):
    #     self.set_prompt(prompts)
    #     return super().open()


class SSHFSInput(QWidget):

    def __init__(
        self,
        preferred_user: str = "",
        preferred_host: str = "",
        preferred_port: int = 22,
        preferred_root: str = "",
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self._build(
            user=preferred_user,
            host=preferred_host,
            port=preferred_port,
            root=preferred_root,
        )

    @property
    def user(self):
        return self._edit_user.text()

    @property
    def host(self):
        return self._edit_host.text()

    @property
    def port(self):
        if not self._edit_port.text():
            return None
        else:
            return int(self._edit_port.text())

    @property
    def root(self):
        return self._edit_root.text()

    @property
    def password(self):
        return self._edit_pw.text()

    @property
    def kbint_responses(self):
        return self._edit_kbint.text()

    def clear(self):
        self._edit_pw.clear()

    def _build(self, user: str = "", host: str = "", port: int = 22, root: str = "/"):
        # Top level layout
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._upper = QHBoxLayout()
        self._middle = QHBoxLayout()
        self._lower = QHBoxLayout()

        # Labels
        self._label_user = QLabel("User:")
        self._label_host = QLabel("Host:")
        self._label_port = QLabel("Port:")
        self._label_root = QLabel("Root:")
        self._label_pw = QLabel("Password:")
        self._label_kbint = QLabel("KB int.:")

        self._edit_user = QLineEdit(user)
        self._edit_host = QLineEdit(host)
        self._edit_port = QLineEdit(str(port))
        self._edit_root = QLineEdit(root)
        self._edit_pw = QLineEdit()
        self._edit_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self._edit_kbint = QLineEdit()

        self._upper.addStretch()
        self._upper.addWidget(self._label_user)
        self._upper.addWidget(self._edit_user)
        self._upper.addWidget(self._label_host)
        self._upper.addWidget(self._edit_host)
        self._upper.addWidget(self._label_port)
        self._upper.addWidget(self._edit_port)
        self._upper.addStretch()

        self._middle.addStretch()
        self._middle.addWidget(self._label_root)
        self._middle.addWidget(self._edit_root)
        self._middle.addStretch()

        self._lower.addStretch()
        self._lower.addWidget(self._label_pw)
        self._lower.addWidget(self._edit_pw)
        self._lower.addWidget(self._label_kbint)
        self._lower.addWidget(self._edit_kbint)
        self._lower.addStretch()

        self._layout.addLayout(self._upper)
        self._layout.addLayout(self._middle)
        self._layout.addLayout(self._lower)

        self.setLayout(self._layout)
