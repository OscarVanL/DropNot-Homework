import os
import shutil
import hashlib
import base64


class ServerFileUtils:
    """
    Utility functions for the server to handle file-related operations
    """

    @staticmethod
    def new_folder(meta_db, target_path, meta):
        """
        Create a new folder in the server sync directory
        :param meta_db: SqliteDict database for tracked file and folder metadata
        :param target_path: Where to sync files to on the server
        :param meta: Metadata for the new folder
        :return: None
        """
        os.makedirs(target_path, exist_ok=True)
        meta_db[target_path] = meta
        meta_db.commit()


    @staticmethod
    def remove_folder(meta_db, target_path):
        """
        Remove folder(s) in the server sync directory
        :param meta_db: SqliteDict database for tracked file and folder metadata
        :param target_path: Where to sync files to on the server
        :return: None
        """
        try:
            meta_db.pop(target_path, None)
            meta_db.commit()
            shutil.rmtree(target_path)
        except FileNotFoundError:
            # The folder might not necessarily be on the server
            pass


    @staticmethod
    def set_file(hash_db, meta_db, target_file, data_dict):
        """
        Create or update a file in the server sync directory
        :param hash_db: SqliteDict database for tracked file MD5 hashes
        :param meta_db: SqliteDict database for tracked file and folder metadata
        :param target_file: File path to create on the server
        :param data_dict: Dictionary containing file binary & metadata
        :return: None
        """
        # Ensure folder structure exists
        os.makedirs(os.path.split(target_file)[0], exist_ok=True)

        # Check if dict contains binary (if not, look up the file contents from the md5 hash map)
        if 'bin' in data_dict:
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
                raise IOError('File', data_dict['path'],
                              'is corrupt (MD5 before transmission and after transmission do not match)')

            hash_db[md5_hash.hexdigest()] = target_file  # Hash -> Path map
            hash_db.commit()
            data_dict.pop('bin', None)  # Remove binary data, only save metadata to DB
            meta_db[target_file] = data_dict  # Path -> Metadata map
            meta_db.commit()
        else:
            # Create file by cloning another file with matching MD5 hash
            duplicate_file_path = hash_db[data_dict['md5']]
            # Copy the identical file into the new file, saving bandwidth :)
            shutil.copyfile(duplicate_file_path, target_file)
            meta_db[target_file] = data_dict
            meta_db.commit()


    @staticmethod
    def remove_file(hash_db, meta_db, target_file):
        """
        Remove a file in the server sync directory
        :param hash_db: SqliteDict database for tracked file MD5 hashes
        :param meta_db: SqliteDict database for tracked file and folder metadata
        :param target_file: File path to create on the server
        :return: None
        """
        try:
            # Remove DB entries for removed file
            md5 = meta_db[target_file]['md5']
            hash_db.pop(md5, None)
            meta_db.pop(target_file, None)
            hash_db.commit()
            meta_db.commit()
            # Remove target file
            os.remove(target_file)
        except OSError:
            # The file might not be on the server if a remove_folder request was completed earlier
            pass
