from flask import Flask
from utils.FileUtils import FileUtils


def start(sync_dir):
    app = Flask(__name__)
    app.run()

    file_manager = FileUtils(sync_dir)

    @app.route('/sync/<path:path>', methods=['POST'])
    def new_item(path):
        print("Syncing new item from client:", path)
        return "Done"


    @app.route('/sync/<path:path>', methods=['PUT'])
    def update_item(path):
        print("Syncing updated file from client:", path)
        return "Done"


    @app.route('/sync/<path:path>', methods=['DELETE'])
    def delete_item(path):
        print("Removing item:", path)
        return "Done"

