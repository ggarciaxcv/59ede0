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

from api import schemas
from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db_scoped
from api.routers.util.uploads import get_cache_file, scan_lines

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
