from flask import Flask, request
from utils.ServerFileUtils import ServerFileUtils
from sqlitedict import SqliteDict
import json
import os
import hashlib
import logging


def initialise(sync_dir):
    # Todo: Upon start verify the hash_db is set correctly for each item within the meta_db?
    app = Flask(__name__)
    #logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename='server.log', level=logging.INFO)
    # A Key-Value DB table storing MD5 -> Path. This allows us to detect the upload of identical files to save bandwidth
    hash_db = SqliteDict('server_tracker.db', tablename='hashmap', encode=json.dumps, decode=json.loads)
    # A Key-Value DB table storing Path -> Metadata. Metadata is stored as JSON
    meta_db = SqliteDict('server_tracker.db', tablename='metadata', encode=json.dumps, decode=json.loads)

    @app.route('/sync/exists/<md5>', methods=['GET'])
    def file_exists_check(md5):
        """
        Allows client to check whether an exact copy of a file exists on the server before uploading.
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
        data = json.loads(request.get_json(silent=False))

        target_path = os.path.normpath(os.path.join(sync_dir, path))
        try:
            if data['type'] == 'file':
                ServerFileUtils.set_file(hash_db, meta_db, target_path, data)
            elif data['type'] == 'folder':
                ServerFileUtils.new_folder(meta_db, target_path, data)
            else:
                return 'Invalid data type received', 400
        except KeyError as e:
            return str(e), 400
        except IOError as e:
            # IOError raised if metadata MD5 does not match received binary content
            print(e)
            return str(e), 422
        return 'OK', 200


    @app.route('/sync/<path:path>', methods=['PUT'])
    def update_item(path):
        data = json.loads(request.get_json(silent=False))

        target_path = os.path.normpath(os.path.join(sync_dir, path))
        try:
            if data['type'] == 'file':
                ServerFileUtils.set_file(hash_db, meta_db, target_path, data)
            else:
                return 'Invalid data type received', 400
        except KeyError as e:
            return str(e), 400
        except IOError as e:
            print(e)
            return e, 422
        return 'OK', 200


    @app.route('/sync/<path:path>', methods=['DELETE'])
    def delete_item(path):
        data = request.get_json(silent=False, force=True)

        target_path = os.path.normpath(os.path.join(sync_dir, path))
        try:
            if data['type'] == 'file':
                ServerFileUtils.remove_file(hash_db, meta_db, target_path)
            elif data['type'] == 'folder':
                ServerFileUtils.remove_folder(meta_db, target_path)
            else:
                return 'Invalid data type received', 400
        except IOError as e:
            print(e)
            return str(e), 422

        return 'OK', 200

    return app
