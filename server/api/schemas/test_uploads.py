import unittest

from api.schemas.uploads import UploadFileSource, UploadCreate

# test UploadFileSource class methods
class TestFileInfo(unittest.TestCase):
    def test_set_file_info(self):
        file = open("./api/testing/prospects.csv", "rb")
        data = UploadFileSource()
        data.set_file_info(file, 16384)
        file.close()

        self.assertEqual(data.get_file_name(), "./api/testing/prospects.csv")
        self.assertEqual(data.get_file_hash(), "97effffc184b4f43c009a71e9f0c8d2c")
        self.assertEqual(data.get_byte_size(), 42538)
        self.assertEqual(data.get_line_count(), 1001)

    def test_set_file_info_2(self):
        file = open("./api/testing/prospects_2.csv", "rb")
        data = UploadFileSource()
        data.set_file_info(file, 16384)
        file.close()

        self.assertEqual(data.get_file_name(), "./api/testing/prospects_2.csv")
        self.assertEqual(data.get_file_hash(), "c8080cfc46a40b7ad214b97bbf124448")
        self.assertEqual(data.get_byte_size(), 426912)
        self.assertEqual(data.get_line_count(), 10001)

    def test_set_file_info_3(self):
        file = open("./api/testing/prospects_empty.csv", "rb")
        data = UploadFileSource()
        data.set_file_info(file, 16384)
        file.close()

        self.assertEqual(data.get_file_name(), "./api/testing/prospects_empty.csv")
        self.assertEqual(data.get_file_hash(), "d41d8cd98f00b204e9800998ecf8427e")
        self.assertEqual(data.get_byte_size(), 0)
        self.assertEqual(data.get_line_count(), 0)


class TestGetHeaderSchema(unittest.TestCase):
    def test_headers_1(self):
        email_ix = 2
        first_ix = 0
        last_ix = 1

        email, first, last = UploadCreate(
            file_name="", file_hash="", byte_size=0, line_count=0, user_id=0
        ).get_header_schema(email_ix, first_ix, last_ix)
        self.assertEqual(email, 2)
        self.assertEqual(first, 0)
        self.assertEqual(last, 1)

    def test_headers_2(self):
        email_ix = 0
        first_ix = 0
        last_ix = 0

        email, first, last = UploadCreate(
            file_name="", file_hash="", byte_size=0, line_count=0, user_id=0
        ).get_header_schema(email_ix, first_ix, last_ix)
        self.assertEqual(email, 0)
        self.assertEqual(first, 1)
        self.assertEqual(last, 2)

    def test_headers_3(self):
        email_ix = 0
        first_ix = 1
        last_ix = 2

        email, first, last = UploadCreate(
            file_name="", file_hash="", byte_size=0, line_count=0, user_id=0
        ).get_header_schema(email_ix, first_ix, last_ix)
        self.assertEqual(email, 0)
        self.assertEqual(first, 1)
        self.assertEqual(last, 2)

    def test_headers_4(self):
        email_ix = 2
        first_ix = 0
        last_ix = 0

        email, first, last = UploadCreate(
            file_name="", file_hash="", byte_size=0, line_count=0, user_id=0
        ).get_header_schema(email_ix, first_ix, last_ix)
        self.assertEqual(email, 2)
        self.assertEqual(first, 0)
        self.assertEqual(last, 1)

    def test_headers_5(self):
        email_ix = 12
        first_ix = 15
        last_ix = 25

        email, first, last = UploadCreate(
            file_name="", file_hash="", byte_size=0, line_count=0, user_id=0
        ).get_header_schema(email_ix, first_ix, last_ix)
        self.assertEqual(email, 12)
        self.assertEqual(first, 15)
        self.assertEqual(last, 25)

    def test_headers_6(self):
        email_ix = 0
        first_ix = 2
        last_ix = 1

        email, first, last = UploadCreate(
            file_name="", file_hash="", byte_size=0, line_count=0, user_id=0
        ).get_header_schema(email_ix, first_ix, last_ix)
        self.assertEqual(email, 0)
        self.assertEqual(first, 2)
        self.assertEqual(last, 1)

    def test_headers_7(self):
        email_ix = 1
        first_ix = 0
        last_ix = 2

        email, first, last = UploadCreate(
            file_name="", file_hash="", byte_size=0, line_count=0, user_id=0
        ).get_header_schema(email_ix, first_ix, last_ix)
        self.assertEqual(email, 1)
        self.assertEqual(first, 0)
        self.assertEqual(last, 2)

    def test_headers_8(self):
        email_ix = 1
        first_ix = 2
        last_ix = 0

        email, first, last = UploadCreate(
            file_name="", file_hash="", byte_size=0, line_count=0, user_id=0
        ).get_header_schema(email_ix, first_ix, last_ix)
        self.assertEqual(email, 1)
        self.assertEqual(first, 2)
        self.assertEqual(last, 0)

    def test_headers_9(self):
        email_ix = 0
        first_ix = 0
        last_ix = 1

        email, first, last = UploadCreate(
            file_name="", file_hash="", byte_size=0, line_count=0, user_id=0
        ).get_header_schema(email_ix, first_ix, last_ix)
        self.assertEqual(email, 0)
        self.assertEqual(first, 2)
        self.assertEqual(last, 1)

    def test_headers_10(self):
        email_ix = 0
        first_ix = 1
        last_ix = 0

        email, first, last = UploadCreate(
            file_name="", file_hash="", byte_size=0, line_count=0, user_id=0
        ).get_header_schema(email_ix, first_ix, last_ix)
        self.assertEqual(email, 0)
        self.assertEqual(first, 1)
        self.assertEqual(last, 2)


if __name__ == "__main__":
    # begin the unittest.main()
    unittest.main()
