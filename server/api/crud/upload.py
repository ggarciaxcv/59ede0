# upload.py contains the CRUD operations for interacting with 
# the Uploads DB table.

from typing import List, Set, Union
from datetime import datetime
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.functions import func
from api import schemas
from api.models import Upload
from api.core.constants import DEFAULT_PAGE_SIZE, DEFAULT_PAGE, MIN_PAGE, MAX_PAGE_SIZE

MAX_SEARCH_RESULTS = 10

class UploadCrud:
    @classmethod
    def get_users_uploads(
        cls,
        db: Session,
        user_id: int,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Union[List[schemas.Upload], None]:
        """Get user's uploads"""
        if page < MIN_PAGE:
            page = MIN_PAGE
        if page_size > MAX_PAGE_SIZE:
            page_size = MAX_PAGE_SIZE
        res = (
            db.query(Upload)
            .filter(
                Upload.user_id == user_id,
            )
            .offset(page * page_size)
            .limit(page_size)
            .all()
        )
        return res

    @classmethod
    def get_user_upload_total(cls, db: Session, user_id: int) -> int:
        return db.query(Upload).filter(Upload.user_id == user_id).count()

    @classmethod
    def create_upload(cls, db: Session, data: schemas.UploadCreate) -> Upload:
        """Create a user upload"""
        upload = Upload(
            file_name=data.file_name, 
            file_hash=data.file_hash, 
            byte_size=data.byte_size, 
            total_count=data.line_count, 
            user_id=data.user_id,
            created=0,
            updated=0,
            skipped=0,
            failed=0,
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)        
        return upload

    # update state of upload object in DB as file is processed
    @classmethod
    def update_upload(cls, db: Session, upload_id: int, created: int, updated: int, skipped: int, failed: int):
        db.query(Upload)\
        .filter(Upload.id == upload_id)\
        .update({
            "created": (Upload.created + created),
            "updated": (Upload.updated + updated),
            "skipped": (Upload.skipped + skipped),
            "failed": (Upload.failed + failed),
            "updated_at": datetime.now(),
            }, synchronize_session="fetch")
        db.commit()
        # db.refresh(res)
        return

    @classmethod
    def get_by_id(cls, db: Session, upload_id: int) -> Union[Upload, None]:
        """Get a single upload by id"""
        return db.query(Upload).filter(Upload.id == upload_id).one_or_none()