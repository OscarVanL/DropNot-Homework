import os
import hashlib
from utils.Metadata import FileEncoding, FolderEncoding, FileMetadata


class FileUtils:

    @staticmethod
    def get_file_metadata(path: str, rel_path: str) -> FileMetadata:
        """
        Get the FileMetadata for a given file path
        :param path: Absolute path of file
        :param rel_path: Relative path from sync dir
        :return: FileMetadata for the file
        """
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
    def get_metadata(encoding: FileEncoding) -> FileMetadata:
        """
        Get the FileMetadata from an existing FileEncoding
        :param encoding: FileEncoding object
        :return: FileMetadata for the FileEncoding
        """
        return FileMetadata(
            path=encoding.path,
            modified=encoding.modified,
            md5=encoding.md5,
            size=encoding.size,
            sync=False)

    @staticmethod
    def get_file_encoding(path, rel_path) -> FileEncoding:
        """
        Get the FileEncoding for a given file path
        :param path: Absolute path of file
        :param rel_path: Relative path from sync dir
        :return: FileEncoding for the file
        """
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
    def get_folder_encoding(path, rel_path) -> FolderEncoding:
        """
        Get the FolderEncoding for a given path
        :param path: Absolute path
        :param rel_path: Relative path from sync dir
        :return: FolderEncoding for the path
        """
        return FolderEncoding(
            path=rel_path,
            modified=os.stat(path).st_mtime,
            sync=False
        )