from flask import Flask, request, jsonify
from utils.FileUtils import FileUtils


def initialise(sync_dir):
    app = Flask(__name__)

    @app.route('/sync/<path:path>', methods=['POST'])
    def new_item(path):
        print("Syncing new item from client:", path)
        meta = request.get_json(silent=False)
        print(meta)
        FileUtils.new_folder(sync_dir, path)
        return "Done"


    @app.route('/sync/<path:path>', methods=['PUT'])
    def update_item(path):
        print("Syncing updated file from client:", path)
        meta = request.get_json()
        print(meta)
        return "Done"


    @app.route('/sync/<path:path>', methods=['DELETE'])
    def delete_item(path):
        print("Removing item:", path)
        meta = request.get_json(silent=False, force=True)
        print(meta)
        return "Done"

    return app

