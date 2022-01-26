import unittest
from requests import post
from io import FileIO

from api import schemas
from api.routers.imports import post_to_upload_service, write_file
from api.core.constants import UPLOAD_SVC_ENDPOINT


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
    payload = {
        "email_index": 0,
        "first_name_index": 0,
        "last_name_index": 0,
        "force": True,
        "has_headers": True,
    }
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


if __name__ == "__main__":
    # begin the unittest.main()
    unittest.main()
