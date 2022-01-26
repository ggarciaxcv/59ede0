import unittest
import threading
from random import randint
from time import sleep

from api.core.threads import ExcThread, CheckActiveThreads

# test threads with similar logic as /api/routers/uploads.scan_lines
class TestThreads(unittest.TestCase):
    # with print statements
    def test_threads_1(self):
        n = 100
        threads = []
        thread_limit = 10
        # test shared variables with Lock
        lock = threading.Lock()
        failed = 0
        for i in range(n):
            t = ExcThread(target=thread_helper, kwargs={"n": i, "limit": 105})
            t.start()
            # test exception handling in threads by adding to threads list
            threads.append(t)
            # test thread limiting
            CheckActiveThreads(thread_limit, 50, 5)

        # catch any exceptions thrown by threads
        # custom join() method raises exception if any
        for t in threads:
            try:
                t.join()
            except ValueError as valErr:
                print(f"Invalid record: {valErr=}, {type(valErr)=}")
                # acquire lock for 'failed' var shared by threads
                lock.acquire()
                failed += 1
                lock.release()
            except BaseException as valErr:
                print(f"ERROR: {valErr=}, {type(valErr)=}")
                # acquire lock for 'failed' var shared by threads
                lock.acquire()
                failed += 1
                lock.release()

        print(f"failed: {failed=}, {type(failed)=}")

    def test_threads_2(self):
        n = 100
        threads = []
        thread_limit = 10
        lock = threading.Lock()
        failed = 0
        for i in range(n):
            t = ExcThread(target=thread_helper_2, args=(i, 200))
            t.start()
            threads.append(t)
            CheckActiveThreads(thread_limit, 50, 5)

        for t in threads:
            try:
                t.join()
            except ValueError as valErr:
                print(f"Invalid record: {valErr=}, {type(valErr)=}")
                # acquire lock for 'failed' var shared by threads
                lock.acquire()
                failed += 1
                lock.release()
            except BaseException as valErr:
                print(f"ERROR: {valErr=}, {type(valErr)=}")
                # acquire lock for 'failed' var shared by threads
                lock.acquire()
                failed += 1
                lock.release()

        print(f"failed: {failed=}, {type(failed)=}")

    def test_threads_3(self):
        n = 100
        threads = []
        thread_limit = 10
        lock = threading.Lock()
        failed = 0
        for i in range(n):
            t = ExcThread(target=thread_helper_2, kwargs={"n": i, "limit": 1000})
            t.start()
            threads.append(t)
            CheckActiveThreads(thread_limit, 50, 5)

        for t in threads:
            try:
                t.join()
            except ValueError as valErr:
                print(f"Invalid record: {valErr=}, {type(valErr)=}")
                # acquire lock for 'failed' var shared by threads
                lock.acquire()
                failed += 1
                lock.release()
            except BaseException as valErr:
                print(f"ERROR: {valErr=}, {type(valErr)=}")
                # acquire lock for 'failed' var shared by threads
                lock.acquire()
                failed += 1
                lock.release()

        print(f"failed: {failed=}, {type(failed)=}")

    def test_threads_4(self):
        n = 100
        threads = []
        thread_limit = 10
        lock = threading.Lock()
        failed = 0
        for i in range(n):
            t = ExcThread(target=thread_helper_2, args=(i, 99))
            t.start()
            threads.append(t)
            CheckActiveThreads(thread_limit, 50, 5)

        for t in threads:
            try:
                t.join()
            except ValueError as valErr:
                print(f"Invalid record: {valErr=}, {type(valErr)=}")
                # acquire lock for 'failed' var shared by threads
                lock.acquire()
                failed += 1
                lock.release()
            except BaseException as valErr:
                print(f"ERROR: {valErr=}, {type(valErr)=}")
                # acquire lock for 'failed' var shared by threads
                lock.acquire()
                failed += 1
                lock.release()

        print(f"failed: {failed=}, {type(failed)=}")


# with print statements (test threads executing in parallel; non-deterministic terminal output)
def thread_helper(n: int, limit: int):
    sleep_time = randint(0, 200) / 1000
    sleep(sleep_time)
    print(n)
    rand = randint(0, limit)
    if rand > 100:
        raise ValueError


# no print statements
def thread_helper_2(n: int, limit: int):
    sleep_time = randint(0, limit) / 1000
    sleep(sleep_time)
    rand = randint(0, limit)
    if rand > 100:
        raise ValueError


if __name__ == "__main__":
    # begin the unittest.main()
    unittest.main()
