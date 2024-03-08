from fsspec import AbstractFileSystem


class Connector:
    FS_TYPE = ""

    def __init__(self, input_widget=None, dialog_widget=None):
        self.input_widget = input_widget
        self.dialog_widget = dialog_widget

    def connect(self, **kwargs) -> tuple[AbstractFileSystem, str]:
        """Connect to the filesystem and return the filesystem object and the root path."""
        pass

    def disconnect(self, **kwargs):
        pass
