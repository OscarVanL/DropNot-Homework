from utils.DirectoryListener import DirectoryListener, ChangeType
from utils.FileUtils import FileUtils
from threading import Thread
from sqlitedict import SqliteDict
import requests
import os
import json

class DropNotClient(Thread):

    def __init__(self, sync_dir, target):
        self.sync_dir = sync_dir
        self.target = target
        # Our key-value stores
        self.file_db = SqliteDict('client_tracker.db', tablename='files', encode=json.dumps, decode=json.loads)
        self.folder_db = SqliteDict('client_tracker.db', tablename='folders', autocommit=True, encode=json.dumps,
                                  decode=json.loads)
        Thread.__init__(self)

    def run(self):
        dir_worker = DirectoryListener(dir=self.sync_dir,
                                       change_callback=self.on_change,
                                       file_db=self.file_db,
                                       folder_db=self.folder_db)
        Thread(name='dir_listener', target=DirectoryListener.scan_directory(dir_worker))


    def on_change(self, change: ChangeType, path):
        # Switch windows path separators to forward slashes for rest URL
        rel_path = os.path.relpath(path, self.sync_dir).replace("\\", "/")

        if change == ChangeType.CreatedFolder:
            print("Folder created: {}".format(path))
            folder_encoding = FileUtils.get_folder_encoding(path, rel_path)
            self.folder_db[path] = repr(folder_encoding)
            # Todo: Handle success/error codes and update sync in folder metadata
            requests.post('http://{}:5000/sync/{}'.format(self.target, rel_path),
                          json=repr(folder_encoding))
        elif change == ChangeType.DeletedFolder:
            print("Folder deleted: {}".format(path))
            self.folder_db.pop(path, None)
            requests.delete('http://{}:5000/sync/{}'.format(self.target, rel_path),
                            json={"type": "folder"})
        elif change == ChangeType.DeletedFile:
            print("File deleted: {}".format(path))
            self.file_db.pop(path, None)
            requests.delete('http://{}:5000/sync/{}'.format(self.target, rel_path),
                            json={"type": "file"})
        elif change == ChangeType.CreatedFile:
            print("File created: {}".format(path))
            file_encoding = FileUtils.get_file_encoding(path, rel_path)
            file_metadata = FileUtils.get_metadata(file_encoding)
            self.file_db[path] = repr(file_metadata)
            requests.post('http://{}:5000/sync/{}'.format(self.target, rel_path),
                          json=repr(file_encoding))
        elif change == ChangeType.ModifiedFile:
            print("File modified: {}".format(path))
            file_encoding = FileUtils.get_file_encoding(path, rel_path)
            file_metadata = FileUtils.get_metadata(file_encoding)
            self.file_db[path] = repr(file_metadata)
            requests.put('http://{}:5000/sync/{}'.format(self.target, rel_path),
                         json=repr(file_encoding))
        else:
            raise RuntimeError('Unsupported ChangeType')

        self.file_db.commit()
        self.folder_db.commit()
