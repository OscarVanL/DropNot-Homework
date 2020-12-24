from utils.DirectoryListener import DirectoryListener, ChangeType
from utils.ClientFileUtils import FileUtils
from threading import Thread
from sqlitedict import SqliteDict
import requests
import os
import json
import logging


class DropNotClient(Thread):

    def __init__(self, sync_dir, target):
        """
        Initialise the DropNot Client
        :param sync_dir: Directory to synchronise on the client machine
        :param target: Target DropNot Server IP/domain
        """
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename='client.log', level=logging.INFO)
        self.sync_dir = sync_dir
        self.target = target
        # Our key-value stores for client metadata
        self.file_db = SqliteDict('client_tracker.db', tablename='files', encode=json.dumps, decode=json.loads)
        self.folder_db = SqliteDict('client_tracker.db', tablename='folders', encode=json.dumps, decode=json.loads)
        Thread.__init__(self)

    def run(self):
        """
        Start the DropNot Client
        :return: None
        """
        # Start a DirectoryListener thread to scan for file changes
        dir_worker = DirectoryListener(dir=self.sync_dir,
                                       change_callback=self.on_change,
                                       file_db=self.file_db,
                                       folder_db=self.folder_db)
        Thread(name='dir_listener', target=DirectoryListener.scan_directory(dir_worker))

    def on_change(self, change: ChangeType, path):
        """
        Handle a change in the synced folder. Callback for the DirectoryListener
        :param change: Value of ChangeType defining what was changed
        :param path: Absolute path of changed file/folder
        :return: None
        """
        # Switch windows path separators to forward slashes for rest URL
        rel_path = os.path.relpath(path, self.sync_dir).replace("\\", "/")

        # Handle change in synced folder
        if change == ChangeType.CreatedFolder:
            self.sync_new_folder(path, rel_path)
        elif change == ChangeType.DeletedFolder:
            self.sync_del_folder(path, rel_path)
        elif change == ChangeType.DeletedFile:
            self.sync_del_file(path, rel_path)
        elif change == ChangeType.CreatedFile:
            self.sync_new_file(path, rel_path)
        elif change == ChangeType.ModifiedFile:
            self.sync_edit_file(path, rel_path)
        else:
            logging.critical('Unsupported ChangeType')
            raise RuntimeError('Unsupported ChangeType')

    def sync_new_folder(self, path, rel_path):
        """
        Synchronise creation of a folder to the server
        :param path: Path including sync directory on Client machine
        :param rel_path: Relative path from sync directory
        :return: None
        """
        folder_encoding = FileUtils.get_folder_encoding(path, rel_path)
        resp = requests.post('http://{}:5000/sync/{}'.format(self.target, rel_path),
                             json=repr(folder_encoding))
        if resp.status_code == 200:
            logging.info('Folder synced to remote:{}'.format(rel_path))
            folder_encoding.sync = True
            self.folder_db[path] = repr(folder_encoding)
            self.folder_db.commit()
        elif resp.status_code == 400 or resp.status_code == 400:
            logging.error('Folder sync unsuccessful{}'.format(rel_path))
            self.folder_db[path] = repr(folder_encoding)
            self.folder_db.commit()
        else:
            logging.critical('Unsupported response status code from remote:{}'.format(resp.status_code))
            raise NotImplementedError('Unsupported resp status code:', resp.status_code)

    def sync_del_folder(self, path, rel_path):
        """
        Synchronise deletion of a folder to the server
        :param path: Path including sync directory on Client machine
        :param rel_path: Relative path from sync directory
        :return: None
        """
        resp = requests.delete('http://{}:5000/sync/{}'.format(self.target, rel_path),
                               json={"type": "folder"})
        if resp.status_code == 200:
            logging.info('Folder removed from remote:{}'.format(rel_path))
            self.folder_db.pop(path, None)
            self.folder_db.commit()
        elif resp.status_code == 400 or resp.status_code == 422:
            logging.error('Folder removal failed on remote:{}'.format(rel_path))
            # todo: handle this?
        else:
            logging.critical('Unsupported response status code from remote:{}'.format(resp.status_code))
            raise NotImplementedError('Unsupported resp status code:', resp.status_code)

    def sync_del_file(self, path, rel_path):
        """
        Synchronise deletion of a file to the server
        :param path: Path including sync directory on Client machine
        :param rel_path: Relative path from sync directory
        :return: None
        """
        resp = requests.delete('http://{}:5000/sync/{}'.format(self.target, rel_path),
                               json={"type": "file"})
        if resp.status_code == 200:
            logging.info('File removed from remote:{}'.format(rel_path))
            self.file_db.pop(path, None)
            self.file_db.commit()
        elif resp.status_code == 400 or resp.status_code == 400:
            logging.error('File removal failed on remote:{}'.format(rel_path))
            # todo: handle this?
        else:
            logging.critical('Unsupported response status code from remote:{}'.format(resp.status_code))
            raise NotImplementedError('Unsupported resp status code:', resp.status_code)

    def sync_new_file(self, path, rel_path):
        """
        Synchronise a new file to the server
        :param path: Path including sync directory on Client machine
        :param rel_path: Relative path from sync directory
        :return: None
        """
        file_encoding = FileUtils.get_file_encoding(path, rel_path)
        file_metadata = FileUtils.get_metadata(file_encoding)

        if self.check_file_exists(file_metadata.md5):
            # Only send metadata, not the binary
            resp = requests.post('http://{}:5000/sync/{}'.format(self.target, rel_path),
                                 json=repr(file_metadata))
        else:
            # Send metadata and binary
            resp = requests.post('http://{}:5000/sync/{}'.format(self.target, rel_path),
                                 json=repr(file_encoding))

        if resp.status_code == 200:
            logging.info('File creation synced to remote:{}'.format(rel_path))
            file_metadata.sync = True
            self.file_db[path] = repr(file_metadata)
            self.file_db.commit()
        elif resp.status_code == 400 or resp.status_code == 422:
            logging.error('File creation sync unsuccessful:{}'.format(rel_path))
            self.file_db[path] = repr(file_metadata)
            self.file_db.commit()
            # todo: handle this?
        else:
            logging.critical('Unsupported response status code from remote:{}'.format(resp.status_code))
            raise NotImplementedError('Unsupported resp status code:', resp.status_code)

    def sync_edit_file(self, path, rel_path):
        """
        Synchronise a file edit to the server
        :param path: Path including sync directory on Client machine
        :param rel_path: Relative path from sync directory
        :return: None
        """
        file_encoding = FileUtils.get_file_encoding(path, rel_path)
        file_metadata = FileUtils.get_metadata(file_encoding)

        if self.check_file_exists(file_metadata.md5):
            # Only send metadata, not the binary
            resp = requests.put('http://{}:5000/sync/{}'.format(self.target, rel_path),
                                json=repr(file_metadata))
        else:
            # Send metadata and binary
            resp = requests.put('http://{}:5000/sync/{}'.format(self.target, rel_path),
                                json=repr(file_encoding))

        if resp.status_code == 200:
            logging.info('File modification synced to remote:{}'.format(rel_path))
            file_metadata.sync = True
            self.file_db[path] = repr(file_metadata)
            self.file_db.commit()
        elif resp.status_code == 400 or resp.status_code == 422:
            logging.info('File modification sync unsuccessful:{}'.format(rel_path))
            self.file_db[path] = repr(file_metadata)
            self.file_db.commit()
            # todo: handle this?
        else:
            logging.critical('Unsupported response status code from remote:{}'.format(resp.status_code))
            raise NotImplementedError('Unsupported resp status code:', resp.status_code)

    def check_file_exists(self, md5):
        """
        Check whether a file matching the md5 already exists on the remote
        :param md5: md5 hash
        :return: True if an identical file exists, False otherwise
        """
        resp = requests.get('http://{}:5000/sync/exists/{}'.format(self.target, md5))
        if resp.status_code == 200:
            return True
        else:
            return False
