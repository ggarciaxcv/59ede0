from typing import List, Set, Union
from sqlalchemy.orm.session import Session
from api import schemas
from api.models import Prospect
from api.core.constants import DEFAULT_PAGE_SIZE, DEFAULT_PAGE, MIN_PAGE, MAX_PAGE_SIZE


class ProspectCrud:
    @classmethod
    def get_users_prospects(
        cls,
        db: Session,
        user_id: int,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Union[List[Prospect], None]:
        """Get user's prospects"""
        if page < MIN_PAGE:
            page = MIN_PAGE
        if page_size > MAX_PAGE_SIZE:
            page_size = MAX_PAGE_SIZE
        return (
            db.query(Prospect)
            .filter(Prospect.user_id == user_id)
            .offset(page * page_size)
            .limit(page_size)
            .all()
        )

    @classmethod
    def get_user_prospects_total(cls, db: Session, user_id: int) -> int:
        return db.query(Prospect).filter(Prospect.user_id == user_id).count()

    @classmethod
    def create_prospect(
        cls, db: Session, user_id: int, data: schemas.ProspectCreate
    ) -> Prospect:
        """Create a prospect"""
        prospect = Prospect(email=data.email, first_name=data.first_name, last_name=data.last_name, user_id=user_id)
        db.add(prospect)
        db.commit()
        db.refresh(prospect)
        return prospect

    @classmethod
    def validate_prospect_ids(
        cls, db: Session, user_id: int, unvalidated_prospect_ids: Set[int]
    ) -> Set[int]:
        res = (
            db.query(Prospect.id)
            .filter(
                Prospect.user_id == user_id, Prospect.id.in_(unvalidated_prospect_ids)
            )
            .all()
        )
        return {row.id for row in res}

    # update Prospect object first_name / last_name when "force" paramater == True in Upload API request
    @classmethod
    def update_prospect(cls, db: Session, user_id: int, prospect_input: schemas.ProspectCreate):
        db.query(Prospect)\
        .filter(Prospect.email == prospect_input.email)\
        .update({
            "first_name": prospect_input.first_name,
            "last_name": prospect_input.last_name,
            }, synchronize_session="fetch")
        db.commit()
        return

    # get prospect by user_id and prospect email
    @classmethod
    def get_by_email(cls, db: Session, user_id: int, email: str) -> Union[Prospect, None]:
        """Get a single upload by id"""
        return db.query(Prospect).filter(Prospect.user_id == user_id).filter(Prospect.email == email).one_or_none()
