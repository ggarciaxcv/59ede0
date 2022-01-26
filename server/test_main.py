# test_main.py is used for integration testing the Uploads feature.
# Tests for the api.routers and api.crud methods were unable to be completed
# with the unittest package due the import error raised by the
# package, which is not present when the program runs.
# This file is ran in conjunction with main.py and a local
# postgre server.
# Note: user_id ('1') must be hard coded in /routers/imports.py and r/outers/uploads.py
# files to run locally.

import unittest
from requests import post
from io import FileIO
from api.core.constants import UPLOAD_SVC_ENDPOINT
from api.core.threads import ExcThread
from api import schemas
from api.routers.imports import post_to_upload_service

# test the /api/prospects_files/import route
# and /api/prospects_files/import/upload (called by Import route)
class TestPostToImports:
    # without overwrite/update
    def test_post_1(self):
        file = open("./cache/prospects.csv", "rb")
        response = post_helper("http://0.0.0.0:3001", False, file)
        print(response)
        file.close()

    # with overwrite/update
    def test_post_2(self):
        file = open("./cache/prospects.csv", "rb")
        response = post_helper("http://0.0.0.0:3001", True, file)
        print(response)
        file.close()


# test the /api/prospects_files/import/upload route
class TestPostToUploads:
    def test_post_1(self):
        response = upload_helper("http://0.0.0.0:3001", False)
        print(response)


# post simulated user request to import service
def post_helper(endpoint: str, force: bool, file: FileIO):
    url = endpoint + "/api/prospects_files/import"
    files = {"file": file}
    payload = {
        "email_index": 2,
        "first_name_index": 0,
        "last_name_index": 0,
        "force": force,
        "has_headers": True,
    }
    response = post(url=url, data=payload, files=files)
    print(response.text)
    return response


# post json request to upload service
def upload_helper(endpoint: str, force: bool):
    url = endpoint + "/api/prospects_files/import/upload"
    write_data = schemas.UploadWriteRequest(
        upload_id=32, file_name="prospects.csv", force=force, has_headers=True
    )
    response = post_to_upload_service(UPLOAD_SVC_ENDPOINT, write_data)
    return response


def main():
    test = TestPostToImports()
    # test = TestPostToUploads()
    # test.test_post_1()
    test.test_post_2()


main()
