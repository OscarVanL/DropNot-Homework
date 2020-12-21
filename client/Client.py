from utils.DirectoryListener import DirectoryListener, ChangeType
from threading import Thread

class DropnotClient():

    def __init__(self, sync_dir):
        dir_worker = DirectoryListener(dir=sync_dir, change_callback=self.on_change)
        Thread(name='dir_listener', target=DirectoryListener.scan_directory(dir_worker))


    def on_change(self, change: ChangeType, path):
        if change == ChangeType.CreatedFolder:
            print("Folder created: {}".format(path))
        elif change == ChangeType.DeletedFolder:
            print("Folder deleted: {}".format(path))
        elif change == ChangeType.CreatedFile:
            print("File created: {}".format(path))
        elif change == ChangeType.DeletedFile:
            print("File deleted: {}".format(path))
        elif change == ChangeType.ModifiedFile:
            print("File modified: {}".format(path))
        else:
            raise RuntimeError('Unsupported ChangeType')