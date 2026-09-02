from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.model import AuthorOrm


class AuthorRepository:
    def __init__(self, db: Session):
        self.db = db

    def ensure_author(self, name: str, email: str) -> AuthorOrm:
        author_obj = self.db.execute(select(AuthorOrm).where(AuthorOrm.email == email)
                                     ).scalar_one_or_none()
        if author_obj:
            return author_obj

        author_obj = AuthorOrm(name=name, email=email)
        self.db.add(author_obj)
        self.db.flush()

        return author_obj


def get_author_repository(db: Session = Depends(get_db)) -> AuthorRepository:
    return AuthorRepository(db)
