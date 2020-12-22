from utils.DirectoryListener import DirectoryListener, ChangeType
from utils.FileUtils import FileUtils
from threading import Thread
import requests
import os


class DropNotClient(Thread):

    def __init__(self, sync_dir, target):
        self.sync_dir = sync_dir
        self.target = target
        Thread.__init__(self)

    def run(self):
        dir_worker = DirectoryListener(dir=self.sync_dir, change_callback=self.on_change)
        Thread(name='dir_listener', target=DirectoryListener.scan_directory(dir_worker))


    def on_change(self, change: ChangeType, path):
        # Switch windows path separators to forward slashes for rest URL
        rel_path = os.path.relpath(path, self.sync_dir).replace("\\", "/")
        if change == ChangeType.CreatedFolder:
            print("Folder created: {}".format(path))
            meta = FileUtils.get_folder_encoding(path, rel_path)
            print(meta)
            requests.post('http://{}:5000/sync/{}'.format(self.target, rel_path),
                          data=str(meta))
        elif change == ChangeType.DeletedFolder:
            print("Folder deleted: {}".format(path))
            requests.delete('http://{}:5000/sync/{}'.format(self.target, rel_path),
                            data={'type': 'folder'})
        elif change == ChangeType.CreatedFile:
            print("File created: {}".format(path))
            requests.post('http://{}:5000/sync/{}'.format(self.target, rel_path),
                          data=FileUtils.get_file_encoding(path, rel_path))
        elif change == ChangeType.DeletedFile:
            print("File deleted: {}".format(path))
            requests.delete('http://{}:5000/sync/{}'.format(self.target, rel_path),
                            data={'type': 'file'})
        elif change == ChangeType.ModifiedFile:
            print("File modified: {}".format(path))
            requests.put('http://{}:5000/sync/{}'.format(self.target, rel_path),
                         data=FileUtils.get_file_encoding(path, rel_path))
        else:
            raise RuntimeError('Unsupported ChangeType')