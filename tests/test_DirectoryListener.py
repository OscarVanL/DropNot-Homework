from unittest.mock import Mock
from sqlitedict import SqliteDict
import unittest
import tempfile
import shutil
import os
import json
from utils.DirectoryListener import DirectoryListener, ChangeType



class TestDirectoryListener(unittest.TestCase):
    def setUp(self):
        # Create temp dir
        self.tmp_dir = tempfile.mkdtemp()
        self.test_dir = os.path.join(self.tmp_dir, 'test')
        self.file_db = SqliteDict(os.path.join(self.tmp_dir, 'temp.db'), tablename='files', encode=json.dumps, decode=json.loads)
        self.folder_db = SqliteDict(os.path.join(self.tmp_dir, 'temp.db'), tablename='folders', encode=json.dumps, decode=json.loads)
        os.mkdir(self.test_dir)

    def tearDown(self):
        self.file_db.close(force=True)
        self.folder_db.close(force=True)
        # Remove temp dir
        shutil.rmtree(self.tmp_dir)

    def test_directory_callback(self):
        callback = Mock()
        listener = DirectoryListener(self.test_dir, callback, self.file_db, self.folder_db)
        new_dir = os.path.join(self.test_dir, 'folderTest')

        # Test CreatedFolder callback called when folder is created
        os.mkdir(new_dir)
        listener.scan_directory(n_iter=1)
        callback.assert_called_with(ChangeType.CreatedFolder, new_dir)
        self.folder_db[new_dir] = json.dumps({})

        # Test DeletedFolder callback called when folder is removed
        os.rmdir(new_dir)
        listener.scan_directory(n_iter=1)
        callback.assert_called_with(ChangeType.DeletedFolder, new_dir)

    def test_file_callback(self):
        callback = Mock()
        listener = DirectoryListener(self.test_dir, callback, self.file_db, self.folder_db)
        new_file = os.path.join(self.test_dir, 'fileTest.txt')
        # Test CreatedFile callback called when file is created
        with open(new_file, 'w') as file:
            file.write('Hello')
        listener.scan_directory(n_iter=1)
        callback.assert_called_with(ChangeType.CreatedFile, new_file)
        self.file_db[new_file] = json.dumps({'modified': 12345})

        # Test ModifiedFile callback called when file is modified
        listener = DirectoryListener(self.test_dir, callback, self.file_db, self.folder_db)
        with open(new_file, 'a') as file:
            file.write('World')
        listener.scan_directory(n_iter=1)
        callback.assert_called_with(ChangeType.ModifiedFile, new_file)

        # Test DeletedFile callback called when file is deleted
        listener = DirectoryListener(self.test_dir, callback, self.file_db, self.folder_db)
        os.remove(new_file)
        listener.scan_directory(n_iter=1)
        callback.assert_called_with(ChangeType.DeletedFile, new_file)


if __name__ == '__main__':
    unittest.main()
