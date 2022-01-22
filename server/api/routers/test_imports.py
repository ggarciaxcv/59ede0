import unittest
from random import randint
from time import sleep
from threading import Lock
from io import FileIO
from fastapi import Depends
from sqlalchemy.orm.session import Session

from api import schemas
from api.core.threads import ExcThread
from api.crud import ProspectCrud
from api.routers.imports import post_to_upload_service, write_file
from api.core.constants import UPLOAD_SVC_ENDPOINT
from api.dependencies.db import get_db

class TestWriteFile(unittest.TestCase):
    def test_write_file_1(self):
        file = open("./api/testing/prospects.csv", "r")
        buffer_size = 16384
        write_file(file, buffer_size)
        file.close()

    def test_write_file_2(self):
        file = open("./api/testing/prospects_2.csv", "r")
        buffer_size = 16384
        write_file(file, buffer_size)
        file.close()

    def test_write_file_3(self):
        file = open("./api/testing/prospects_empty.csv", "r")
        buffer_size = 16384
        write_file(file, buffer_size)
        file.close()

class TestPostToImports(unittest.TestCase):
    def test_post_1(self):
        file = open("./api/testing/prospects.csv", "rb")
        response = post_to_upload_service("http://0.0.0.0:3001", file)
        print(response)
        file.close()

# post user request to upload service
def post_helper(endpoint: str, file: FileIO):
    url = endpoint + "/api/prospects_files/import"
    files = {"file": file}
    payload ={"email_index": 0, "first_name_index": 0, "last_name_index": 0, "force": True, "has_headers": True}
    headers = {"Content-Type": "multipart/form-data"}
    response = post(url=url, data=payload, files=files, headers=headers) 
    print(response)
    return response

class TestPostToUploadService(unittest.TestCase):
    def test_post_2(self):
        file = open("./api/testing/prospects.csv", "rb")
        write_data = schemas.UploadWriteRequest(upload_id=123, file_hash="abc123")
        # write_data.set_file_info()
        write_data.set_options(False, False)
        response = post_to_upload_service(UPLOAD_SVC_ENDPOINT, write_data, file)
        print(response)
        file.close()


# test failed due to ImportError (circular import)
# /api/crud/user.py imports api.core.security
#   UserCrud.create_user() references security.get_password_hash()
# /api/core/security.py imports api.crud.user.UserCrud
#   authenticate_user() references UserCrud.get_user_by_email()
class TestCreateProspect(unittest.TestCase):
    def test_create_prospect_1(self):
        test_id = 12345
        email = "ggarciaxcv@gmail.com"
        first = "Gilberto"
        last = "Garcia"
        prospect_input = schemas.ProspectCreate(email=email, first_name=first, last_name=last)
        
        db = Depends(get_db)
        prospect = ProspectCrud.create_prospect(db, test_id, prospect_input)
        if(prospect is None):
            print("error: no prospect created!")
        
        print(prospect.id)
        print(prospect.created_at)
        print(prospect.updated_at)

        self.assertEqual(prospect.email, email)
        self.assertEqual(prospect.first_name, first)
        self.assertEqual(prospect.last_name, last)