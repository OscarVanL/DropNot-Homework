import os
import shutil
import hashlib
import base64
import json


class ServerFileUtils:
    @staticmethod
    def new_folder(meta_db, target_path, meta):
        os.makedirs(target_path, exist_ok=True)
        meta_db[target_path] = meta
        meta_db.commit()


    @staticmethod
    def remove_folder(meta_db, target_path):
        try:
            shutil.rmtree(target_path)
            meta_db.pop(target_path, None)
            meta_db.commit()
        except FileNotFoundError:
            # The folder might not be on the server
            meta_db.pop(target_path, None)
            meta_db.commit()
            pass


    @staticmethod
    def set_file(hash_db, meta_db, target_file, data_dict):
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
            data_dict.pop('bin', None)  # Remove binary data, only save metadata to DB
            meta_db[target_file] = data_dict  # Path -> Metadata map
            hash_db.commit()
            meta_db.commit()
        else:
            # Create file by searching for file with matching MD5 hash
            print("Inbound dictionary does not contain binary data, checking MD5 hash map")
            duplicate_file_path = hash_db[data_dict['md5']]
            print("Matches file:", duplicate_file_path)
            # Copy the identical file into the new file, saving bandwidth :)
            shutil.copyfile(duplicate_file_path, target_file)


    @staticmethod
    def remove_file(hash_db, meta_db, target_path):
        try:
            # Remove target file
            os.remove(target_path)
            # Remove DB entries for removed file
            md5 = json.loads(meta_db[target_path])['md5']
            hash_db.pop(md5, None)
            meta_db.pop(target_path, None)
            hash_db.commit()
            meta_db.commit()
        except OSError:
            # The file might not be on the server
            pass
