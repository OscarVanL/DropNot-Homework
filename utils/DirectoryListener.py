import os
import time


class DirectoryListener:
    file_meta = -1
    folder_meta = -1

    def __init__(self, dir, change_callback):
        self.dir = dir
        self.change_callback = change_callback

    def scan_directory(self, n_iter=-1):
        while n_iter != 0:
            file_meta_new = {}
            folder_meta_new = set()

            # Walk the entire folder structure within the directory
            for dir, subdirs, files in os.walk(self.dir):
                # Create a set of all folders
                folder_meta_new.add(dir)

                for fname in files:
                    fpath = os.path.join(dir, fname)
                    # Create a dict of the last modified time for each file
                    file_meta_new[fpath] = os.stat(fpath).st_mtime

            # Scan for folder changes (excluding first scan on start)
            if self.folder_meta != -1:
                self.find_diff_folders(folder_meta_new)
            self.folder_meta = folder_meta_new

            # Scan for file changes (excluding first scan on start)
            if self.file_meta != -1:
                self.find_diff_files(file_meta_new)
            self.file_meta = file_meta_new

            time.sleep(5)
            n_iter -= 1


    def find_diff_folders(self, folders_after: set):
        # Check for folder creation and removal
        removed = self.folder_meta - folders_after
        created = folders_after - self.folder_meta
        for folder in removed:
            self.change_callback(ChangeType.DeletedFolder, folder)

        for folder in created:
            self.change_callback(ChangeType.CreatedFolder, folder)


    def find_diff_files(self, files_after: dict):
        # Check for file creation and removal
        removed = self.file_meta.keys() - files_after.keys()
        created = files_after.keys() - self.file_meta.keys()
        for file in removed:
            self.change_callback(ChangeType.DeletedFile, file)

        for file in created:
            self.change_callback(ChangeType.CreatedFile, file)

        # Check for file modifications
        for file, modified in files_after.items():
            try:
                if modified != self.file_meta[file]:
                    self.change_callback(ChangeType.ModifiedFile, file)
            except KeyError:
                # If it's a new file it'll result in a KeyError as the existing file_meta won't have tracked it yet
                pass


class ChangeType(set):
    CreatedFile, DeletedFile, ModifiedFile, CreatedFolder, DeletedFolder = range(0, 5)