from dataclasses import dataclass
import json
import base64


@dataclass
class FileMetadata:
    """
    Represent a file's metadata and serialise it to a JSON string
    """
    path: str
    modified: float
    md5: str
    size: int
    sync: False  # Whether the item is synced to the server, false by default.

    # Define JSON representation for REST transmission
    def __repr__(self):
        return json.dumps({
            'path': self.path,
            'modified': self.modified,
            'md5': self.md5,
            'size': self.size,
            'type': 'file',
            'sync': self.sync
        })


@dataclass
class FileEncoding:
    """
    Represent a file's binary content + metadata, and serialise it to a JSON string
    """
    bin: bytes
    path: str
    modified: float
    md5: str
    size: int

    # Define JSON representation for REST transmission
    def __repr__(self):
        return json.dumps({
            'bin': base64.b64encode(self.bin).decode('ascii'),
            'path': self.path,
            'modified': self.modified,
            'md5': self.md5,
            'size': self.size,
            'type': 'file'
        })


@dataclass
class FolderEncoding:
    """
    Represent a folder's relative path from sync directory and metadata
    """
    path: str
    modified: float
    sync: False  # Whether the item is synced to the server, false by default.

    # Define JSON representation for REST transmission
    def __repr__(self):
        return json.dumps({
            'path': self.path,
            'modified': self.modified,
            'type': 'folder',
            'sync': self.sync
        })