from dataclasses import dataclass
import json
import base64


@dataclass
class FileMetadata:
    path: str
    modified: float
    md5: str
    size: int
    sync: False

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
    path: str
    modified: float
    sync: False

    # Define JSON representation for REST transmission
    def __repr__(self):
        return json.dumps({
            'path': self.path,
            'modified': self.modified,
            'type': 'folder',
            'sync': self.sync
        })