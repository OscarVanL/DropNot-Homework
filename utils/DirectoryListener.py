import os
import time

class DirectoryListener():
    file_meta = None
    folder_meta = None

    def __init__(self, dir, change_callback):
        self.dir = dir
        self.change_callback = change_callback

    def scan_directory(self):
        while True:
            file_meta_new = {}
            folder_meta_new = set()

            for dir, subdirs, files in os.walk(self.dir):
                folder_meta_new.add(dir)
                for fname in files:
                    fpath = os.path.join(dir, fname)
                    file_meta_new[fpath] = os.stat(fpath).st_mtime

            if self.folder_meta:
                self.find_diff_folders(folder_meta_new)
            self.folder_meta = folder_meta_new

            if self.file_meta:
                self.find_diff_files(file_meta_new)
            self.file_meta = file_meta_new

            time.sleep(10)


    def find_diff_folders(self, folders_after: set):
        removed = self.folder_meta - folders_after
        created = folders_after - self.folder_meta
        for folder in removed:
            self.change_callback(ChangeType.DeletedFolder, folder)

        for folder in created:
            self.change_callback(ChangeType.CreatedFolder, folder)


    def find_diff_files(self, files_after: dict):
        removed = self.file_meta.keys() - files_after.keys()
        created = files_after.keys() - self.file_meta.keys()
        for file in removed:
            self.change_callback(ChangeType.DeletedFile, file)

        for file in created:
            self.change_callback(ChangeType.CreatedFile, file)

        for file, modified in files_after.items():
            try:
                if modified != self.file_meta[file]:
                    self.change_callback(ChangeType.ModifiedFile, file)
            except KeyError:
                # If it's a new file it'll result in a KeyError as the existing file_meta won't have tracked it yet
                pass



class ChangeType(set):
    CreatedFile, DeletedFile, ModifiedFile, CreatedFolder, DeletedFolder = range(0, 5)