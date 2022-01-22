import unittest
from random import randint
from time import sleep
from threading import Lock
from io import FileIO

from api import schemas
from api.crud.upload import UploadCrud
from api.database import get_db

# fails -- import error (circular import)
# note: not present when called from main.py
def TestCreateUpload(unittest.TestCase):
    def test_create_upload_1(self):
        file = open("./api/testing/prospects.csv", "rb")
        db = get_db()

        # initialize upload object
        file_info = schemas.UploadFileSource()
        file_info.set_file_info(file, 16384)
        file.close()

        # write upload to DB
        upload_input = schemas.UploadCreate(
            file_info.get_file_name(),
            file_info.get_file_hash(),
            file_info.get_byte_size(),
            file_info.get_line_count(),
            current_user.id,
        )

        upload = UploadCrud.create_upload(db, upload_inpupt)

        print(upload)
