import os
import hashlib
import base64
import shutil
from utils.Metadata import FileEncoding, FolderEncoding, FileMetadata


class FileUtils:
    @staticmethod
    def new_folder(sync_dir, path):
        new_dir = os.path.join(sync_dir, path)
        os.makedirs(new_dir, exist_ok=True)

    @staticmethod
    def remove_folder(sync_dir, path):
        rm_dir = os.path.join(sync_dir, path)
        try:
            shutil.rmtree(rm_dir)
        except FileNotFoundError:
            # The folder might not be on the server
            pass

    @staticmethod
    def set_file(sync_dir, path, data_dict):
        target_file = os.path.join(sync_dir, path)
        # Ensure folder structure exists
        os.makedirs(os.path.split(target_file)[0], exist_ok=True)
        # Create file from binary
        md5_hash = hashlib.md5()
        with open(target_file, 'wb+') as file:
            bytes = base64.b64decode(data_dict['bin'])
            file.write(bytes)
            # Read back file and verify MD5 to ensure it transferred correctly
            file.seek(0)
            md5_hash.update(file.read())

        # Set 'modified' metadata for file
        os.utime(target_file, (data_dict['modified'], data_dict['modified']))

        # Verify MD5 of file to ensure it transferred correctly
        if md5_hash.hexdigest() != data_dict['md5']:
            raise IOError('File', path, 'is corrupt (MD5 before and after do not match)')

    @staticmethod
    def remove_file(sync_dir, path):
        rm_file = os.path.join(sync_dir, path)
        try:
            os.remove(rm_file)
        except OSError:
            # The file might not be on the server
            pass

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