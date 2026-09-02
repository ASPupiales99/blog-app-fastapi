from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.model import TagOrm


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def ensure_tag(self, name: str) -> TagOrm:
        tag_obj = self.db.execute(
            select(TagOrm).where(TagOrm.name.ilike(name))
        ).scalar_one_or_none()

        if tag_obj:
            return tag_obj

        tag_obj = TagOrm(name=name)
        self.db.add(tag_obj)
        self.db.flush()

        return tag_obj


def get_tag_repository(db: Session = Depends(get_db)) -> TagRepository:
    return TagRepository(db)
