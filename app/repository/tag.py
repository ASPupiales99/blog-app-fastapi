from typing import Optional

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.model import TagOrm, PostOrm, post_tags
from app.schema.tag import TagPublic
from app.service.pagination import paginate_query


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_tag(self, name: str) -> TagOrm:
        tag_obj = TagOrm(name=name)
        self.db.add(tag_obj)
        self.db.flush()

        return tag_obj

    def get_tag_by_name(self, name: str) -> Optional[TagOrm]:
        normalize = name.strip().lower()

        tag_obj = self.db.execute(
            select(TagOrm).where(func.lower(TagOrm.name) == normalize)
        ).scalar_one_or_none()

        return tag_obj

    def ensure_tag(self, name: str) -> TagOrm:
        tag_obj = self.get_tag_by_name(name)
        if tag_obj:
            return tag_obj

        return self.create_tag(name=name)

    def search_tags(
            self,
            search: Optional[str],
            order_by: str = "id",
            direction: str = "asc",
            page: int = 1,
            per_page: int = 10
    ):
        query = select(TagOrm)
        if search:
            query = query.where(func.lower(TagOrm.name).ilike(f"%{search.lower()}%"))

        allowed_order = {
            "id": TagOrm.id,
            "name": func.lower(TagOrm.name),
        }

        result = paginate_query(
            db=self.db,
            model=TagOrm,
            base_query=query,
            page=page,
            per_page=per_page,
            order_by=order_by,
            direction=direction,
            allowed_order=allowed_order
        )

        result["items"] = [TagPublic.model_validate(item) for item in result["items"]]

        return result

    def get_tag_by_id(self, tag_id: int) -> Optional[TagOrm]:
        tag_db = select(TagOrm).where(TagOrm.id == tag_id)
        return self.db.execute(tag_db).scalar_one_or_none()

    def update_tag(self, tag_id: int, name: str) -> Optional[TagOrm]:
        tag_db = self.get_tag_by_id(tag_id)

        if not tag_db:
            return None

        if name is not None:
            tag_db.name = name.strip().lower()

        self.db.add(tag_db)
        self.db.flush()
        self.db.refresh(tag_db)

        return tag_db

    def delete_tag(self, tag_id: int) -> bool:
        tag_db = self.get_tag_by_id(tag_id)

        if not tag_db:
            return False

        self.db.delete(tag_db)

        return True

    def get_most_popular_tag(self) -> dict | None:
        row = (
            self.db.execute(
                select(
                    TagOrm.id.label("id"),
                    TagOrm.name.label("name"),
                    func.count(PostOrm.id).label("uses")
                )
                .join(post_tags, post_tags.c.tag_id == TagOrm.id)
                .join(PostOrm, PostOrm.id == post_tags.c.post_id)
                .group_by(TagOrm.id, TagOrm.name)
                .order_by(func.count(PostOrm.id).desc(), func.lower(TagOrm.name).asc())
                .limit(1)
            )
            .mappings()
            .first()
        )

        return dict(row) if row else None


def get_tag_repository(db: Session = Depends(get_db)) -> TagRepository:
    return TagRepository(db)
