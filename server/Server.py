from flask import Flask, request, jsonify
from utils.FileUtils import FileUtils
import json


def initialise(sync_dir):
    app = Flask(__name__)

    @app.route('/sync/<path:path>', methods=['POST'])
    def new_item(path):
        print("Syncing new item from client:", path)
        data = json.loads(request.get_json(silent=False))

        try:
            if data['type'] == 'file':
                FileUtils.set_file(sync_dir, path, data)
            elif data['type'] == 'folder':
                FileUtils.new_folder(sync_dir, path)
            else:
                return 'Invalid data type received', 400
        except IOError as e:
            print(e)
            return str(e), 422
        return 'OK', 200


    @app.route('/sync/<path:path>', methods=['PUT'])
    def update_item(path):
        print("Syncing updated file from client:", path)
        data = json.loads(request.get_json(silent=False))

        try:
            if data['type'] == 'file':
                FileUtils.set_file(sync_dir, path, data)
            else:
                return 'Invalid data type received', 400
        except IOError as e:
            print(e)
            return e, 422
        return 'OK', 200


    @app.route('/sync/<path:path>', methods=['DELETE'])
    def delete_item(path):
        print("Removing item:", path)
        data = request.get_json(silent=False, force=True)

        try:
            if data['type'] == 'file':
                FileUtils.remove_file(sync_dir, path)
            elif data['type'] == 'folder':
                FileUtils.remove_folder(sync_dir, path)
            else:
                return 'Invalid data type received', 400
        except IOError as e:
            print(e)
            return e, 422
        return 'OK', 200

    return app

