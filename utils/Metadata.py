from dataclasses import dataclass
import json

@dataclass
class FileMetadata:
    bin: bin
    path: str
    modified: float
    md5: str
    size: int

    # Define JSON representation for REST transmission
    def __repr__(self):
        return json.dumps({
            'bin': self.bin,
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