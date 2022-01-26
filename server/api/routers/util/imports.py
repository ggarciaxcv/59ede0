from requests import post
from os import path, makedirs
from shutil import copyfileobj

from fastapi import UploadFile
from api import schemas

# write_file writes the given file to the disk cache
def write_file(file: UploadFile, user_id: int, buffer_size: int):
    txt = "./cache/{:n}"
    copy_dir = path.normcase(txt.format(user_id))
    exists = path.exists(copy_dir)
    if not exists:
        makedirs(copy_dir)
        print("created directory: %s", copy_dir)

    copy_path = path.normcase(copy_dir + "/" + path.basename(file.filename))
    copy = open(copy_path, "wb")
    copyfileobj(file.file, copy, buffer_size)
    copy.close()

    print("file %s copied to cache", copy.name)
    return copy_path


# post user request to upload service
def post_to_upload_service(endpoint: str, data: schemas.UploadWriteRequest):
    url = endpoint + "/api/prospects_files/import/upload"
    response = post(
        url=url,
        json={
            "upload_id": data.upload_id,
            "file_name": data.file_name,
            "email_index": data.email_index,
            "first_name_index": data.first_name_index,
            "last_name_index": data.last_name_index,
            "force": data.force,
            "has_headers": data.has_headers,
        },
    )
    print(response)  # logging only
    return response
