import unittest
import shutil
import tempfile
import os
import json
import hashlib
from sqlitedict import SqliteDict
from server import Server
from utils.Metadata import FileEncoding


class TestServer(unittest.TestCase):
    def setUp(self):
        # Create test dir
        self.tmp_dir = tempfile.mkdtemp()
        self.test_dir = os.path.join(self.tmp_dir, 'test')
        os.mkdir(self.test_dir)
        self.meta_db = SqliteDict(os.path.join(self.tmp_dir, 'temp.db'), tablename='metadata', encode=json.dumps,
                                  decode=json.loads)
        self.hash_db = SqliteDict(os.path.join(self.tmp_dir, 'temp.db'), tablename='hashmap', encode=json.dumps,
                                  decode=json.loads)
        # Launch Flask server in test client mode
        self.server = Server.initialise(self.test_dir, self.hash_db, self.meta_db).test_client()
        self.server.testing = True

    def tearDown(self):
        self.meta_db.close(force=True)
        self.hash_db.close(force=True)
        # Remove temp dir
        shutil.rmtree(self.test_dir)

    # file_exists() gives 200 if requested file hash exists
    def test_file_exists_200(self):
        # Create a mock file
        file_path = os.path.join(self.test_dir, 'testFile1.txt')
        md5_hash = hashlib.md5()
        with open(file_path, 'w') as file:
            file.write('Hello World')

        # Add mock file's MD5 to hash DB
        with open(file_path,  'rb') as file:
            md5_hash.update(file.read())
            md5 = md5_hash.hexdigest()
        self.hash_db[md5] = file_path

        # Check 200 response is given when checking for file's existence
        resp = self.server.get('/sync/exists/{}'.format(md5))
        self.assertEqual(200, resp.status_code)

    # file_exists() gives 204 if requested hash does not exist
    def test_file_exists_204(self):
        resp = self.server.get('/sync/exists/INVALID-MD5')
        self.assertEqual(204, resp.status_code)

    # new_item() gives 200 if provided request was valid
    def test_new_item_200(self):
        file = os.path.join(self.test_dir, 'test_new_item_200.txt')
        encoding = FileEncoding(bin=b'ABC123', path='example/path', modified=1608675488.0458164, md5='bbf2dead374654cbb32a917afd236656', size=6)
        resp = self.server.post('/sync/{}'.format(file), json=repr(encoding))
        self.assertEqual(200, resp.status_code)

    # new_item() gives 400 if an invalid metadata filetype is given
    def test_new_item_400(self):
        new_item_invalid = json.dumps({
            'path': 'example/path',
            'modified': 100000.00,
            'type': 'invaid-type',
            'sync': False})
        resp = self.server.post('/sync/example/path', json=new_item_invalid)
        self.assertEqual(400, resp.status_code)

    # new_item() gives 422 error if new file's received binary does not match MD5
    def test_new_item_422(self):
        item = FileEncoding(bin=b'HELLOWORLD',
                            path='example/path/file.txt',
                            modified=1608675488.0458164,
                            md5='NOT-MATCHING-BIN',
                            size=10)
        resp = self.server.post('/sync/{}'.format(item.path), json=repr(item))
        self.assertEqual(422, resp.status_code)

    # update_item() gives 200 if provided request was valid
    def test_update_item_200(self):
        # Create an item to update
        file = os.path.join(self.test_dir, 'test_update_item_200.txt')
        encoding = FileEncoding(bin=b'ABC123', path='example/path', modified=1608675488.0458164, md5='bbf2dead374654cbb32a917afd236656', size=6)
        self.server.post('/sync/{}'.format(file), json=repr(encoding))

        # Update this item with new content
        encoding_new = FileEncoding(bin=b'HelloWorld', path='example/path', modified=1608675488.0458164, md5='68e109f0f40ca72a15e05cc22786f8e6', size=10)
        resp = self.server.post('/sync/{}'.format(file), json=repr(encoding_new))
        self.assertEqual(200, resp.status_code)

    # update_item() gives 400 if invalid type is given
    def test_update_item_400(self):
        # update_item does not accept folders, only files
        new_item_invalid = json.dumps({
            'path': 'example/path',
            'modified': 100000.00,
            'type': 'folder',
            'sync': False})
        resp = self.server.put('/sync/example/path', json=new_item_invalid)
        self.assertEqual(400, resp.status_code)

    # update_item() gives 422 if received file's binary does not match MD5
    def test_update_item_422(self):
        item = FileEncoding(bin=b'HELLOWORLD',
                            path='example/path/file.txt',
                            modified=1608675488.0458164,
                            md5='NOT-MATCHING-BIN',
                            size=10)
        resp = self.server.put('/sync/{}'.format(item.path), json=repr(item))
        self.assertEqual(422, resp.status_code)

    # delete_item() gives 200 if provided request was valid
    def test_delete_item_200(self):
        # Create an item to remove
        file = os.path.join(self.test_dir, 'test_update_item_200.txt')
        encoding = FileEncoding(bin=b'ABC123', path='example/path', modified=1608675488.0458164, md5='bbf2dead374654cbb32a917afd236656', size=6)
        self.server.post('/sync/{}'.format(file), json=repr(encoding))

        # Remove the item
        item_json = {'type': 'file'}
        resp = self.server.delete('/sync/{}'.format(file), json=item_json)
        self.assertEqual(200, resp.status_code)

    # delete_item() gives 400 if invalid type is given
    def test_delete_item_400(self):
        # delete_item only allows for deletion of 'folder' and 'file' types
        item_json = {'type': 'invalid-type'}
        resp = self.server.delete('/sync/example/path', json=item_json)
        self.assertEqual(400, resp.status_code)

    # delete_item() requests for items that do not exist on the server.
    # This shouldn't raise any exceptions or errors, as the server remains in the state the client expects.
    def test_delete_item_does_not_exist(self):
        folder_json = {'type': 'folder'}
        resp = self.server.delete('/sync/example/path/nonexistent', json=folder_json)
        self.assertEqual(200, resp.status_code)

        file_json = {'type': 'file'}
        resp = self.server.delete('/sync/example/path/nonexistent/file.txt', json=file_json)
        self.assertEqual(200, resp.status_code)

