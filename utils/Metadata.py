from dataclasses import dataclass
import json
import base64


@dataclass
class FileMetadata:
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
class FolderMetadata:
    path: str
    modified: float

    # Define JSON representation for REST transmission
    def __repr__(self):
        return json.dumps({
            'path': self.path,
            'modified': self.modified,
            'type': 'folder'
        })