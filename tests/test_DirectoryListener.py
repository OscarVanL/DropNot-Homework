import unittest
import tempfile
import shutil
import os
from utils.DirectoryListener import DirectoryListener, ChangeType
from unittest.mock import Mock
import time

class TestDirectoryListener(unittest.TestCase):
    def setUp(self):
        # Create temp dir
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove temp dir
        shutil.rmtree(self.test_dir)

    def test_directory_callback(self):
        callback = Mock()
        listener = DirectoryListener(dir=self.test_dir, change_callback=callback)
        listener.scan_directory(n_iter=1)
        new_dir = os.path.join(self.test_dir, 'folderTest')

        # Test CreatedFolder callback called when folder is created
        os.mkdir(new_dir)
        listener.scan_directory(n_iter=1)
        callback.assert_called_with(ChangeType.CreatedFolder, new_dir)

        # Test DeletedFolder callback called when folder is removed
        os.rmdir(new_dir)
        listener.scan_directory(n_iter=1)
        callback.assert_called_with(ChangeType.DeletedFolder, new_dir)

    def test_file_callback(self):
        callback = Mock()
        listener = DirectoryListener(dir=self.test_dir, change_callback=callback)
        listener.scan_directory(n_iter=1)
        new_file = os.path.join(self.test_dir, 'fileTest.txt')
        # Test CreatedFile callback called when file is created
        with open(new_file, 'w') as file:
            file.write('Hello')
        listener.scan_directory(n_iter=1)
        callback.assert_called_with(ChangeType.CreatedFile, new_file)

        # Test ModifiedFile callback called when file is modified
        with open(new_file, 'a') as file:
            file.write('World')
        listener.scan_directory(n_iter=1)
        callback.assert_called_with(ChangeType.ModifiedFile, new_file)

        # Test DeletedFile callback called when file is deleted
        os.remove(new_file)
        listener.scan_directory(n_iter=1)
        callback.assert_called_with(ChangeType.DeletedFile, new_file)


if __name__ == '__main__':
    unittest.main()
