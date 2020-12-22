import os
import hashlib
from utils.Metadata import FileMetadata, FolderMetadata


class FileUtils:


    @staticmethod
    def new_folder(sync_dir, path):
        new_dir = os.path.join(sync_dir, path)
        print("Creating folder(s):", new_dir)
        os.makedirs(new_dir, exist_ok=True)

    @staticmethod
    def get_file_encoding(path, rel_path):

        md5_hash = hashlib.md5()
        with open(path, 'rb') as f:
            md5_hash.update(f)
            return FileMetadata(bin=f.read(),
                                path=rel_path,
                                modified=os.stat(path).st_mtime,
                                md5=md5_hash.hexdigest(),
                                size=os.stat(path).st_size)

    @staticmethod
    def get_folder_encoding(path, rel_path):
        return FolderMetadata(
            path=rel_path,
            modified=os.stat(path).st_mtime
        )