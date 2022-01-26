# uploads.py contains the operations for the Upload service to parse
# and upload new Prospects to the DB from the CSV file.

# In production, I would decouple the operations by first uploading the .csv file
# to a file storage service, then sending a notification to the Uploads
# service to retrieve and process the file. An example of this implementation would
# be uploading the file to AWS S3, then using a service such as gRPC or AWS SNS to call
# the Uploads service to retrieve the file from S3 and process the information. The HTTP
# response would be returned asynchrounously to the client after the S3 upload is complete,
# while the file is processed by the Uploads service in the background. This feature could
# be further optimized by adding a notification service to alert the user once the upload is complete.

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm.session import Session
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from io import FileIO
from os import path
from threading import Lock
from pydantic import EmailStr

from api import schemas
from api.dependencies.auth import get_current_user
from api.core import threads
from api.crud import ProspectCrud, UploadCrud
from api.dependencies.db import get_db_scoped

router = APIRouter(prefix="/api", tags=["prospects_files"])

# process upload request from stored file
@router.post(
    "/prospects_files/import/upload", response_model=schemas.UploadCreateResponse
)
def new_upload_write(
    data: schemas.UploadWriteRequest,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db_scoped),
):
    print("*** NEW UPLOAD REQUEST ***")
    """Validate and add prospects to a campaign"""
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Please log in")

    # write file to disk cache
    print("retrieving cache file")
    try:
        cache_file = get_cache_file(current_user.id, data.file_name)
    except BaseException as err:
        print(f"get cache file failed: {err=}, {type(err)=}")
        raise HTTPException(status_code=500, detail="Something went wrong!")

    # scan file and write Prospect records to DB
    print("uploading records...")
    err = scan_lines(
        cache_file,
        current_user.id,
        data.upload_id,
        data.email_index,
        data.first_name_index,
        data.last_name_index,
        data.force,
        data.has_headers,
        db,
    )

    # return response
    message = "Upload complete!"
    if err:
        message = "Upload completed with some errors."
        return JSONResponse(
            {"success": True, "message": message, "id": data.upload_id}, 201
        )

    print("*** UPLOAD COMPLTE ***")
    return JSONResponse(
        {"success": True, "message": message, "id": data.upload_id}, 201
    )


# write_file writes the given file to the disk cache
def get_cache_file(user_id: int, file_name: str) -> FileIO:
    txt = "./cache" + "/{:n}/" + file_name
    file_path = path.normcase(txt.format(user_id))
    exists = path.exists(file_path)
    if not exists:
        print("file not found: %s", file_path)
        raise

    cache_file = open(file_path, "rb")
    return cache_file


# scan_lines scans each line in the .csv file
def scan_lines(
    file: FileIO,
    user_id: int,
    upload_id: int,
    email_index: int,
    first_name_index: int,
    last_name_index: int,
    force: bool,
    headers: bool,
    db: Session,
) -> bool:
    # scan lines in file
    lines = file.readlines()
    (created, updated, skipped, failed) = (0, 0, 0, 0)

    thread_limit = 25  # max number of concurrent threads
    lock = Lock()  # lock for 'failed' var shared by threads
    threads_list = []  # list of threads
    for i, line in enumerate(lines):
        if headers == True and i == 0:
            # skip first line if has headers
            continue

        # start new thread for write Prospect to DB operation if active threads < limit
        t = threads.ExcThread(
            target=parse_prospect,
            args=(
                line.strip().decode("utf-8"),
                upload_id,
                user_id,
                email_index,
                first_name_index,
                last_name_index,
                force,
            ),
        )
        t.start()
        threads_list.append(t)
        threads.CheckActiveThreads(thread_limit, 50, 5)

        if i % 100 == 0:
            txt = "records processed: {:n}"
            print(txt.format(i))

        # catch any exceptions raised in threads and increment fail count if exception
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
        try:
            upload = UploadCrud.update_upload(
                db, upload_id, created, updated, skipped, failed
            )
            return True
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise
    # no errors during db upload
    return False


# parse line from CSV file, create Prospect object and write to DB
def parse_prospect(
    line: str,
    upload_id: int,
    user_id: int,
    email_index: int,
    first_name_index: int,
    last_name_index: int,
    force: bool,
):
    spl = line.split(",")
    if len(spl) != 3:
        # raise exception for invalid CSV record
        print("FAIL: " + line)
        raise ValueError

    try:
        email = EmailStr(spl[email_index])
        first_name = spl[first_name_index]
        last_name = spl[last_name_index]
        prospect_input = schemas.ProspectCreate(
            email=EmailStr(spl[email_index]).lower(),
            first_name=spl[first_name_index],
            last_name=spl[last_name_index],
        )
        write_prospect(upload_id, user_id, prospect_input, force)
    except BaseException as err:
        print("FAIL: " + spl[email_index].lower())
        print(f"Unexpected {err=}, {type(err)=}")
        raise


# write Prospect object to DB
def write_prospect(
    upload_id: int,
    user_id: int,
    prospect: schemas.ProspectCreate,
    force: bool,
):
    # these values are used to update counts in Upload DB object
    (created, updated, skipped, failed) = (0, 0, 0, 0)

    # get scoped local SQA session for thread
    db = next(get_db_scoped())
    # check if process exists and perform corresponding write operation
    # (note: would change to conditional write in prod but unsure how to do in SQL Alchemy)
    prospect_db = ProspectCrud.get_by_email(db, user_id, prospect.email)

    # update prospect if force == True and prospect already exists
    if prospect_db is None:
        # create new prospect
        try:
            ProspectCrud.create_prospect(db, user_id, prospect)
            created += 1
        except BaseException as err:
            db.close()
            db.remove()
            print(f"prospect create failed: {err=}, {type(err)=}")
            raise
    else:  # update existing or skip
        if force:
            # update existing if force == True
            try:
                ProspectCrud.update_prospect(db, user_id, prospect)
                updated += 1
            except BaseException as err:
                db.close()
                db.remove()
                print(f"prospect update failed: {err=}, {type(err)=}")
                raise
        else:
            # skip update existing if force != True
            skipped += 1

    # update upload object
    # (note: this could be optimized by writing both the
    # Prospect and Upload objects in a transaction, but
    # not sure how to do in SQA)
    try:
        UploadCrud.update_upload(db, upload_id, created, updated, skipped, failed)
    except BaseException as err:
        db.close()
        db.remove()
        print(f"update upload failed: {err=}, {type(err)=}")
        raise

    db.close()
    db.remove()
    return
