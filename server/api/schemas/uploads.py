# uploads.py contains the Schema Classes for Upload service operations.
# Classes in this file are references by both /api/routers/imports.py
# and /api/routers/uploads.py.

import hashlib

from datetime import datetime
from typing import Optional
from io import FileIO
from os import path

from pydantic import BaseModel
from fastapi import Form

# Upload represents the processed CSV file upload information
# stored in the database.
class Upload(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_hash: str
    byte_size: int
    created: int
    updated: int
    skipped: int
    failed: int
    total_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# UploadCreate contains default information for intitializing Upload objects in the Uploads db table.
class UploadCreate(BaseModel):
    file_name: str
    file_hash: str
    byte_size: int
    line_count: int
    user_id: int

# UploadCreateRequest represents the POST request data sent to the Import endpoint by the end user.
class UploadCreateRequest(BaseModel):
    email_index: int
    first_name_index: Optional[int]
    last_name_index: Optional[int]
    force: Optional[bool]
    has_headers: Optional[bool]

    @classmethod
    def as_form(
        cls, 
        email_index: int = Form(...),
        first_name_index: Optional[int] = Form(...),
        last_name_index: Optional[int] = Form(...),
        force: Optional[bool] = Form(...),
        has_headers: Optional[bool] = Form(...),
    ) -> 'UploadWriteRequest':
        return cls(email_index=email_index, first_name_index=first_name_index, last_name_index=last_name_index, force=force, has_headers=has_headers)

# UploadWriteRequest contains info sent to the Uploads service
# by the Import service after a new UploadCreateRequest is made by a user.
class UploadWriteRequest(BaseModel):
    upload_id: int
    file_name: str
    force: Optional[bool]
    has_headers: Optional[bool]

# UploadCreateResponse represents the data returned to the user after a new upload request is created.
class UploadCreateResponse(BaseModel):
    id: int
    file_hash: str
    success: bool
    message: str

# UploadFileSource contains temporary file data for use while processing new Uploads.
# Omits pydantic.BaseModel as io.FileIO is not compatible with pydantic validation.
# Additionally, pydantic is not required as this data structure is only used locally 
# by the Import service and is not sent across the network.
class UploadFileSource():
    file_name: str
    file_hash: str
    byte_size: int
    line_count: int

    # derive file info from file with arbitrary byte size buffer
    @classmethod
    def set_file_info(self, file: FileIO, chunk_size: int):
        # set file name
        self.file_name = path.basename(file.name)

        # set hash and file size
        size = 0
        hash = hashlib.md5()
        file.seek(0)
        chunk = file.read(chunk_size)
        while chunk:
            hash.update(chunk)
            size += len(chunk)
            chunk = file.read(chunk_size)

        self.file_hash = hash.hexdigest()
        self.byte_size = size

        # set line count
        file.seek(0)
        lines = file.readlines()

        self.line_count = len(lines)

    @classmethod
    def get_file_name(self) -> str:
        return self.file_name

    @classmethod
    def get_file_hash(self) -> str:
        return self.file_hash

    @classmethod
    def get_byte_size(self) -> int:
        return self.byte_size

    @classmethod
    def get_line_count(self) -> int:
        return self.line_count

# UploadStatusResponse represents the response for GET requests to /api/prospects_files/:id/progress.
# 'done' field represents the total number of records created, updated, or skipped.
class UploadStatusResponse(BaseModel):
    total: int
    done: int
