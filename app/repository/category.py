from typing import Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.model import CategoryOrm


class CategoryRepository:
    def __init__(self, db: Session = Depends(get_db)) -> None:
        self.db = db

    def list_many(self, *, skip: int = 0, limit: int = 50) -> Sequence[CategoryOrm]:
        query = select(CategoryOrm).offset(skip).limit(limit)
        return self.db.execute(query).scalars().all()

    def list_with_total(self, *, page: int = 1, per_page: int = 50) -> tuple[int, list[CategoryOrm]]:
        pass

    def get(self, category_id: int) -> CategoryOrm | None:
        return self.db.get(CategoryOrm, category_id)

    def get_by_slug(self, slug: str) -> CategoryOrm | None:
        query = select(CategoryOrm).where(CategoryOrm.slug == slug)
        return self.db.execute(query).scalars().first()

    def create(self, *, name: str, slug: str) -> CategoryOrm:
        category = CategoryOrm(name=name, slug=slug)

        self.db.add(category)
        self.db.flush()
        self.db.refresh(category)

        return category

    def update(self, category: CategoryOrm, updates: dict) -> CategoryOrm:
        for key, value in updates.items():
            setattr(category, key, value)

        self.db.add(category)
        self.db.flush()

        return category

    def delete(self, category: CategoryOrm) -> None:
        self.db.delete(category)


def get_category_repository(db: Session = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)
