import unittest
from random import randint
from time import sleep
from threading import Lock
from io import FileIO

from api import schemas
from api.core import threads
from api.routers.uploads import get_cache_file


class TestGetCacheFile(unittest.TestCase):
    def test_get_file_1(self):
        name = "prospects.csv"
        user_id = 123
        file = get_cache_file(user_id, name)
        print(file.name)
        file.close()
        self.assertEqual("./cache/123/prospects.csv", file.name)


class TestScanLines(unittest.TestCase):
    def test_scan_lines_1(self):
        file = open("./api/testing/prospects.csv", "rb")
        scan_lines_helper(file, True, False)
        file.close()

    def test_scan_lines_2(self):
        file = open("./api/testing/prospects_2.csv", "rb")
        scan_lines_helper(file, True, False)
        file.close()

    def test_scan_lines_3(self):
        file = open("./api/testing/prospects_empty.csv", "rb")
        scan_lines_helper(file, True, False)
        file.close()


# scan_lines scans each line in the .csv file
def scan_lines_helper(
    file: FileIO,
    force: bool,
    headers: bool,
):
    # scan lines in file
    file.seek(0)
    lines = file.readlines()
    (created, updated, skipped, failed) = (0, 0, 0, 0)

    thread_limit = 25  # max number of concurrent threads
    lock = Lock()  # lock for 'failed' var shared by threads
    threads_list = []  # list of threads
    for i, line in enumerate(lines):
        if headers == True & i == 0:
            # skip first line if has headers
            continue

        # start new thread for write Prospect to DB operation if active threads < limit
        threads.CheckActiveThreads(thread_limit, 50, 5)
        t = threads.ExcThread(
            target=parse_prospect_helper,
            args=(
                line.strip().decode("utf-8"),
                force,
            ),
        )
        t.start()
        threads_list.append(t)

        for t in threads_list:
            try:
                t.join()
            except ValueError as valErr:
                print(f"Invalid record: {valErr=}, {type(valErr)=}")
                # acquire lock for 'failed' var shared by threads
                lock.acquire()
                failed += 1
                lock.release()
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                lock.acquire()
                failed += 1
                lock.release()

    file.close()

    # update upload object if failed
    if failed > 0:
        print("upload object fail count updated")
        print(failed)


# parse line from CSV file, create Prospect object and write to DB
def parse_prospect_helper(line: str, force: bool):
    spl = line.split(",")
    if len(spl) != 3:
        # raise exception for invalid CSV record
        print("FAILED: " + line)
        raise ValueError

    # note: fixed file schema: last_name, first_name, email
    try:
        prospect = schemas.ProspectCreate(
            email=spl[2], first_name=spl[1], last_name=spl[0]
        )
        message = (
            prospect.email + " | " + prospect.last_name + ", " + prospect.first_name
        )
        print(message)
    except BaseException as err:
        print("FAIL: " + spl[2])
        print(err)


if __name__ == "__main__":
    # begin the unittest.main()
    unittest.main()
