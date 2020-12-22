import unittest
import tempfile
import shutil
import os
import hashlib

from utils.FileUtils import FileUtils


class TestFileUtils(unittest.TestCase):
    def setUp(self):
        # Create test dir
        self.test_dir = tempfile.mkdtemp()
        # Create test file
        self.test_file = os.path.join(self.test_dir, 'testFile.txt')
        with open(self.test_file, 'w') as file:
            file.write("abc123")

        # Calculate md5 hash
        with open(self.test_file, 'rb') as file:
            md5_hash = hashlib.md5()
            md5_hash.update(file.read())
            self.expected_md5 = md5_hash.hexdigest()

        # Find expected modified time and file size
        self.expected_folder_modified = os.stat(self.test_dir).st_mtime
        self.expected_file_modified = os.stat(self.test_file).st_mtime
        self.expected_size = os.stat(self.test_file).st_size

    def tearDown(self):
        # Remove temp dir
        shutil.rmtree(self.test_dir)

    # Verify all fields are set correctly for file encodings
    def test_get_file_encoding(self):
        metadata = FileUtils.get_file_encoding(self.test_file, self.test_file)
        self.assertEqual(b'abc123', metadata.bin)
        self.assertEqual(self.test_file, metadata.path)
        self.assertEqual(self.expected_file_modified, metadata.modified)
        self.assertEqual(self.expected_size, metadata.size)
        self.assertEqual(self.expected_md5, metadata.md5)

    # Verify all fields are set correctly for folder encodings
    def test_get_folder_encoding(self):
        metadata = FileUtils.get_folder_encoding(self.test_dir, self.test_dir)
        self.assertEqual(self.test_dir, metadata.path)
        self.assertEqual(self.expected_folder_modified, metadata.modified)