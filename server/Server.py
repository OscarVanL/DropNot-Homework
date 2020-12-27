from flask import Flask, request
from utils.ServerFileUtils import ServerFileUtils
from sqlitedict import SqliteDict
import json
import os
import hashlib
import logging


def initialise(sync_dir, hash_db=None, meta_db=None):
    """
    Application Factory method for Flask
    :param sync_dir: Directory to sync files to
    :param hash_db: (optional): Use non-default hash DB (used for Unit testing)
    :param meta_db: (optional): Use non-default metadata DB (used for Unit testing)
    :return: Flask app
    """
    app = Flask(__name__)

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename='server.log', level=logging.INFO)

    if hash_db is None:
        # A Key-Value DB table storing MD5 -> Path. This allows us to detect the upload of identical files to save bandwidth
        hash_db = SqliteDict('server_tracker.db', tablename='hashmap', encode=json.dumps, decode=json.loads)
    if meta_db is None:
        # A Key-Value DB table storing Path -> Metadata. Metadata is stored as JSON
        meta_db = SqliteDict('server_tracker.db', tablename='metadata', encode=json.dumps, decode=json.loads)

    @app.route('/sync/exists/<md5>', methods=['GET'])
    def file_exists_check(md5):
        """
        Allows clients to check whether an exact copy of a file exists on the server before uploading.
        :param md5: md5 of file to check
        :return: 200 if exist, 204 if it doesn't
        """
        try:
            existing_path = hash_db[md5]

            # Check stored MD5 hash is still up-to-date
            md5_hash = hashlib.md5()
            with open(existing_path, 'rb') as file:
                md5_hash.update(file.read())

            if md5 == md5_hash.hexdigest():
                logging.info('File with identical MD5 found on the server:{}'.format(existing_path))
                return 'Already exists', 200
            else:
                # If the DB's stored MD5 map does not match the file's actual MD5
                # (This could happen if the file was modified server-side after it was originally synced)
                hash_db.pop(md5, None)
                hash_db[md5_hash.hexdigest()] = existing_path
                hash_db.commit()
                return 'Does not exist', 204
        except KeyError:
            # Give response 204 to say a copy of the file doesn't already exist
            return 'Does not exist', 204
        except FileNotFoundError:
            return 'Does not exist', 204

    @app.route('/sync/<path:path>', methods=['POST'])
    def new_item(path):
        """
        Create a new file or folder on the server
        :param path: Target folder/file path from the route URL
        :return: 200 success. 400 invalid request. 422 file corrupted in transmission.
        """
        data = json.loads(request.get_json(silent=False))

        target_path = os.path.normpath(os.path.join(sync_dir, path))
        try:
            if data['type'] == 'file':
                ServerFileUtils.set_file(hash_db, meta_db, target_path, data)
                logging.info('File created:{}'.format(path))
            elif data['type'] == 'folder':
                ServerFileUtils.new_folder(meta_db, target_path, data)
                logging.info('Folder created:{}'.format(path))
            else:
                return 'Invalid data type received', 400
        except KeyError as e:
            return str(e), 400
        except IOError as e:
            # IOError raised if metadata MD5 does not match received binary content
            logging.warning('IOError when creating new file or folder. '
                            'This is thrown if the MD5 checksum does not match a file. '
                            'This may be because of corruption during transmission')
            return str(e), 422
        return 'OK', 200

    @app.route('/sync/<path:path>', methods=['PUT'])
    def update_item(path):
        """
        Update an edited file on the server
        :param path: Target folder/file path from the route URL
        :return: 200 success. 400 invalid request. 422 file corrupted in transmission.
        """
        data = json.loads(request.get_json(silent=False))
        target_path = os.path.normpath(os.path.join(sync_dir, path))
        try:
            if data['type'] == 'file':
                ServerFileUtils.set_file(hash_db, meta_db, target_path, data)
                logging.info('File updated:{}'.format(path))
            else:
                return 'Invalid data type received', 400
        except KeyError as e:
            return str(e), 400
        except IOError as e:
            logging.warning('IOError when creating editing a file.'
                            'This is thrown if the MD5 checksum does not match a file. '
                            'This may be because of corruption during transmission')
            return str(e), 422
        return 'OK', 200

    @app.route('/sync/<path:path>', methods=['DELETE'])
    def delete_item(path):
        """
        Delete a file on the server
        :param path: Target folder/file path from the route URL
        :return: 200 success. 400 invalid request. 422 IO error on server
        """
        data = request.get_json(silent=False, force=True)
        target_path = os.path.normpath(os.path.join(sync_dir, path))

        try:
            if data['type'] == 'file':
                ServerFileUtils.remove_file(hash_db, meta_db, target_path)
                logging.info('File removed:{}'.format(path))
            elif data['type'] == 'folder':
                ServerFileUtils.remove_folder(meta_db, target_path)
                logging.info('Folder removed:{}'.format(path))
            else:
                return 'Invalid data type received', 400
        except IOError as e:
            logging.warning('IOError when deleting a file or folder.')
            return str(e), 422

        return 'OK', 200

    return app
