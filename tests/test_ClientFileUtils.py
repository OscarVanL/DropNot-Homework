import unittest
import tempfile
import shutil
import os
import hashlib

from utils.Metadata import FileEncoding
from utils.ClientFileUtils import FileUtils


class TestClientFileUtils(unittest.TestCase):
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

    def test_get_file_metadata(self):
        meta = FileUtils.get_file_metadata(self.test_file, self.test_file)
        self.assertEqual(self.test_file, meta.path)
        self.assertEqual(self.expected_file_modified, meta.modified)
        self.assertEqual(self.expected_size, meta.size)
        self.assertEqual(self.expected_md5, meta.md5)
        self.assertEqual(False, meta.sync)

    def test_get_metadata(self):
        input_encoding = FileEncoding(b'abc123', self.test_file, 12345.00, 'ABC123AA00', 128)
        meta = FileUtils.get_metadata(input_encoding)
        self.assertEqual(self.test_file, meta.path)
        self.assertEqual(12345.00, meta.modified)
        self.assertEqual('ABC123AA00', meta.md5)
        self.assertEqual(128, meta.size)
        self.assertEqual(False, meta.sync)

    # Verify all fields are set correctly for file encodings
    def test_get_file_encoding(self):
        encoding = FileUtils.get_file_encoding(self.test_file, self.test_file)
        self.assertEqual(b'abc123', encoding.bin)
        self.assertEqual(self.test_file, encoding.path)
        self.assertEqual(self.expected_file_modified, encoding.modified)
        self.assertEqual(self.expected_size, encoding.size)
        self.assertEqual(self.expected_md5, encoding.md5)

    # Verify all fields are set correctly for folder encodings
    def test_get_folder_encoding(self):
        metadata = FileUtils.get_folder_encoding(self.test_dir, self.test_dir)
        self.assertEqual(self.test_dir, metadata.path)
        self.assertEqual(self.expected_folder_modified, metadata.modified)