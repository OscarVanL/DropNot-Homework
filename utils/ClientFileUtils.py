import os
import hashlib
from utils.Metadata import FileEncoding, FolderEncoding, FileMetadata


class FileUtils:

    @staticmethod
    def get_file_metadata(path: str, rel_path: str):
        md5_hash = hashlib.md5()
        with open(path, 'rb') as f:
            md5_hash.update(f.read())
            f.seek(0)
            return FileMetadata(path=rel_path,
                                modified=os.stat(path).st_mtime,
                                md5=md5_hash.hexdigest(),
                                size=os.stat(path).st_size,
                                sync=False)

    @staticmethod
    def get_metadata(encoding: FileEncoding):
        return FileMetadata(
            path=encoding.path,
            modified=encoding.modified,
            md5=encoding.md5,
            size=encoding.size,
            sync=False)

    @staticmethod
    def get_file_encoding(path, rel_path):
        md5_hash = hashlib.md5()
        with open(path, 'rb') as f:
            md5_hash.update(f.read())
            f.seek(0)
            return FileEncoding(bin=f.read(),
                                path=rel_path,
                                modified=os.stat(path).st_mtime,
                                md5=md5_hash.hexdigest(),
                                size=os.stat(path).st_size)

    @staticmethod
    def get_folder_encoding(path, rel_path):
        return FolderEncoding(
            path=rel_path,
            modified=os.stat(path).st_mtime,
            sync=False
        )