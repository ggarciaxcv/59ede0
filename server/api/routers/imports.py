# imports.py receives requests sent to the /api/prospects_files/ endpoints.
# The file is cached on the disk (in place of file storage service) for use by the Uploads service,
# while file info is sent to the Uploads service to retrieve the file for asynchronous processing.
# A success message and the upload summary info are returned to the user while the file.
# is processed downstream.
# Upload read requests (/progress) are processed synchronously in this file.

from fastapi import APIRouter, HTTPException, status, Depends, Form, File, UploadFile
from sqlalchemy.orm.session import Session
from starlette.responses import JSONResponse
from starlette import status
from typing import Optional

from api import schemas
from api.dependencies.auth import get_current_user
from api.core.constants import UPLOAD_SVC_ENDPOINT
from api.core.threads import ExcThread
from api.crud import UploadCrud
from api.dependencies.db import get_db
from api.routers.util.imports import write_file, post_to_upload_service

router = APIRouter(prefix="/api", tags=["prospects_files"])

# get upload progress by checking DB object current state
@router.get(
    "/prospects_files/{upload_id}/progress", response_model=schemas.UploadStatusResponse
)
def get_upload_progress(
    upload_id: str,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get upload by id"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )
    upload = UploadCrud.get_by_id(db, upload_id)
    if upload is None:
        # requested upload not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested Upload was not found.",
        )
    if upload.user_id != current_user.id:
        # current user not authorized to view requested upload
        # owned by another user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view the requested Upload.",
        )
    done = upload.created + upload.skipped + upload.updated + upload.failed
    return {"total": upload.total_count, "done": done}


# start new file upload
# actual upload completed by sending upload info
# to Upload service while response is sent to end user
@router.post("/prospects_files/import", response_model=schemas.UploadCreateResponse)
def new_upload_request(
    file: UploadFile = File(...),
    email_index: int = Form(...),
    first_name_index: Optional[int] = Form(0),
    last_name_index: Optional[int] = Form(0),
    force: Optional[bool] = Form(False),
    has_headers: Optional[bool] = Form(False),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate and create new Upload object"""
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Please log in")

    # write file to disk cache
    try:
        file_name = write_file(file, current_user.id, 16384)
        file = open(file_name, "rb")
    except BaseException as err:
        print(f"write file failed: {err=}, {type(err)=}")
        raise HTTPException(status_code=500, detail="Something went wrong!")

    # initialize upload object
    file_info = schemas.UploadFileSource()
    file_info.set_file_info(file, 16384)
    file.close()

    # write upload to DB
    upload_input = schemas.UploadCreate(
        file_name=file_info.get_file_name(),
        file_hash=file_info.get_file_hash(),
        byte_size=file_info.get_byte_size(),
        line_count=file_info.get_line_count(),
        user_id=current_user.id,
    )
    upload = UploadCrud.create_upload(db, upload_input)

    # get file header schema & send file info to upload service with thread
    email_ix, first_ix, last_ix = upload_input.get_header_schema(
        email_index, first_name_index, last_name_index
    )
    write_data = schemas.UploadWriteRequest(
        upload_id=upload.id,
        file_name=upload.file_name,
        email_index=email_ix,
        first_name_index=first_ix,
        last_name_index=last_ix,
        force=force,
        has_headers=has_headers,
    )
    t = ExcThread(target=post_to_upload_service, args=(UPLOAD_SVC_ENDPOINT, write_data))
    t.start()

    # return success response to user
    return JSONResponse(
        {
            "success": True,
            "message": "Upload iniated!",
            "file_hash": file_info.get_file_hash(),
            "id": upload.id,
        },
        201,
    )
