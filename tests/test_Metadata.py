import unittest
from utils.Metadata import FileMetadata, FileEncoding, FolderEncoding


class TestMetadata(unittest.TestCase):
    def test_init_file_metadata(self):
        meta = FileMetadata('test/path/example.txt', 12345.00, 'ABC00AA123', 128, False)
        self.assertEqual('test/path/example.txt', meta.path)
        self.assertEqual(12345.00, meta.modified)
        self.assertEqual('ABC00AA123', meta.md5)
        self.assertEqual(128, meta.size)
        self.assertEqual(False, meta.sync)

    def test_repr_file_metadata(self):
        meta = FileMetadata('test/path', 12345.00, 'ABC00AA123', 128, False)
        self.assertEqual('{"path": "test/path", "modified": 12345.0, "md5": "ABC00AA123", "size": 128, "type": "file", "sync": false}',
                         repr(meta))

    def test_init_file_encoding(self):
        encoding = FileEncoding(b'ABC123', 'test/path/example.txt', 12345.00, 'ABC00AA123', 128)
        self.assertEqual(b'ABC123', encoding.bin)
        self.assertEqual('test/path/example.txt', encoding.path)
        self.assertEqual(12345.00, encoding.modified)
        self.assertEqual('ABC00AA123', encoding.md5)
        self.assertEqual(128, encoding.size)

    def test_repr_file_encoding(self):
        encoding = FileEncoding(b'ABC123', 'test/path/example.txt', 12345.00, 'ABC00AA123', 128)
        self.assertEqual('{"bin": "QUJDMTIz", "path": "test/path/example.txt", "modified": 12345.0, "md5": "ABC00AA123", "size": 128, "type": "file"}',
                         repr(encoding))

    def test_init_folder_encoding(self):
        encoding = FolderEncoding('test/path', 12345.00, False)
        self.assertEqual('test/path', encoding.path)
        self.assertEqual(12345.00, encoding.modified)
        self.assertEqual(False, encoding.sync)

    def test_repr_folder_encoding(self):
        encoding = FolderEncoding('test/path', 12345.00, False)
        self.assertEqual('{"path": "test/path", "modified": 12345.0, "type": "folder", "sync": false}',
                         repr(encoding))
