import unittest

from api.schemas.uploads import UploadFileSource

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
        

if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()