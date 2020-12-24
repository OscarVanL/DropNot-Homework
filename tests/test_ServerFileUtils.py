import unittest
import tempfile
import os
import shutil
import json
import hashlib
import filecmp
from sqlitedict import SqliteDict
from utils.ServerFileUtils import ServerFileUtils

class TestServerFileUtils(unittest.TestCase):

    def setUp(self):
        # Create temp dir
        self.tmp_dir = tempfile.mkdtemp()
        self.test_dir = os.path.join(self.tmp_dir, 'test')
        self.meta_db = SqliteDict(os.path.join(self.tmp_dir, 'temp.db'), tablename='metadata', encode=json.dumps, decode=json.loads)
        self.hash_db = SqliteDict(os.path.join(self.tmp_dir, 'temp.db'), tablename='hashmap', encode=json.dumps, decode=json.loads)
        os.mkdir(self.test_dir)

    def tearDown(self):
        self.meta_db.close(force=True)
        self.hash_db.close(force=True)
        # Remove temp dir
        shutil.rmtree(self.tmp_dir)

    def test_new_folder(self):
        meta_str = json.dumps({'test1': 'value1'})
        new_folder_test = os.path.join(self.test_dir, 'test1', 'test1')
        ServerFileUtils.new_folder(self.meta_db, new_folder_test, meta_str)
        self.assertTrue(os.path.exists(new_folder_test))
        self.assertEqual({'test': 'value'}, json.loads(self.meta_db[new_folder_test]))

    def test_remove_folder(self):
        # Create a mock folder & metadata to remove
        meta_str = json.dumps({'test2': 'value2'})
        test_dir = os.path.join(self.test_dir, 'test2', 'test2')
        self.meta_db[test_dir] = meta_str

        ServerFileUtils.remove_folder(self.meta_db, test_dir)

        self.assertFalse(os.path.exists(test_dir))
        # Check metadata has been removed
        with self.assertRaises(KeyError):
            str = self.meta_db[test_dir]


    def test_set_file(self):
        test_file = os.path.join(self.test_dir, 'parent', 'test3.txt')
        data_dict = {
            'bin': 'QUJDMTIz',  # 'ABC123' encoded in base64
            'path': 'example/path',
            'modified': 1608675488.0458164,
            'md5': 'bbf2dead374654cbb32a917afd236656',
            'size': 6
        }
        ServerFileUtils.set_file(self.hash_db, self.meta_db, test_file, data_dict)

        # Check metadata DB has been set correctly
        self.assertEqual(data_dict, self.meta_db[test_file])
        # Check hashmap DB has been set correctly
        self.assertEqual(test_file, self.hash_db['bbf2dead374654cbb32a917afd236656'])

        # Check content is correct once decoded from base64
        with open(test_file, 'r') as file:
            val = file.read()
            self.assertEqual('ABC123', val)

        # Check md5 matches before and after
        md5_hash = hashlib.md5()
        with open(test_file, 'rb') as file:
            md5_hash.update(file.read())
            self.assertEqual('bbf2dead374654cbb32a917afd236656', md5_hash.hexdigest())

        # Check file modified has been set correctly.
        self.assertAlmostEqual(1608675488.0458164, os.stat(test_file).st_mtime)

    # This test simulates a file with binary content that was corrupted in transmission
    def test_set_file_corrupt_ioerror(self):
        test_file = os.path.join(self.test_dir, 'parent', 'test4.txt')
        data_dict = {
            'bin': 'QUJDMTIz',  # 'ABC123' encoded in base64
            'path': 'example/path',
            'modified': 1608675488.0458164,
            'md5': 'md5-doesnt-match',
            'size': 6
        }
        with self.assertRaises(OSError):
            ServerFileUtils.set_file(self.hash_db, self.meta_db, test_file, data_dict)

    # This test simulates the feature that set_file will clone files with matching MD5s even if binary data is missing
    def test_set_file_md5_match(self):
        # Write a file normally
        file = os.path.join(self.test_dir, 'parent', 'test5.txt')
        dict = {
            'bin': 'QUJDMTIz',  # 'ABC123' encoded in base64
            'path': 'example/path',
            'modified': 1608675488.0458164,
            'md5': 'bbf2dead374654cbb32a917afd236656',
            'size': 6
        }
        ServerFileUtils.set_file(self.hash_db, self.meta_db, file, dict)

        # Write another file, with no binary data, but the same md5
        test_file = os.path.join(self.test_dir, 'parent', 'test6.txt')
        test_dict = {
            'md5': 'bbf2dead374654cbb32a917afd236656',
        }
        ServerFileUtils.set_file(self.hash_db, self.meta_db, test_file, test_dict)

        # The two files should be identical in content, as the content of test6.txt is inferred from the MD5 match
        self.assertTrue(filecmp.cmp(file, test_file))

    def test_remove_file(self):
        # Write a file normally
        file = os.path.join(self.test_dir, 'parent', 'test7.txt')
        dict = {
            'bin': 'QUJDMTIz',  # 'ABC123' encoded in base64
            'path': 'example/path',
            'modified': 1608675488.0458164,
            'md5': 'bbf2dead374654cbb32a917afd236656',
            'size': 6
        }
        ServerFileUtils.set_file(self.hash_db, self.meta_db, file, dict)

        # Remove the file
        ServerFileUtils.remove_file(self.hash_db, self.meta_db, file)
        # Check it's removed
        self.assertFalse(os.path.isfile(file))
        # Check hash DB's value is gone
        with self.assertRaises(KeyError):
            val = self.hash_db['bbf2dead374654cbb32a917afd236656']
        # Check metatata DB's value is gone
        with self.assertRaises(KeyError):
            meta = self.meta_db[file]
