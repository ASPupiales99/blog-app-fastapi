from math import ceil
from typing import Optional, Tuple, List

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload, joinedload

from app.core.db import get_db
from app.model import PostOrm, TagOrm, User
from app.repository import TagRepository
from app.repository.tag import get_tag_repository


class PostRepository:
    def __init__(self, db: Session, tag_repository: TagRepository):
        self.db = db
        self.tag_repository = tag_repository

    def get_post(self, post_id: int) -> Optional[PostOrm]:
        post_find = select(PostOrm).where(PostOrm.id == post_id)
        return self.db.execute(post_find).scalar_one_or_none()

    def search_posts(self, query: Optional[str], order_by: str, direction: str, page: int, per_page: int) -> Tuple[
        int, List[PostOrm]]:

        results = select(PostOrm)

        if query:
            results = results.where(PostOrm.title.ilike(f"%{query}%"))

        total = self.db.scalar(select(func.count()).select_from(results.subquery())) or 0

        if total == 0:
            return 0, []

        current_page = min(page, max(1, ceil(total / per_page)))

        order_col = PostOrm.id if order_by == "id" else func.lower(PostOrm.title)

        results = results.order_by(order_col.asc() if direction == "asc" else order_col.desc())

        start = (current_page - 1) * per_page
        items = self.db.execute(results.limit(per_page).offset(start)).scalars().all()

        return total, items

    def get_posts_by_tags(self, tags: List[str]) -> List[PostOrm]:

        normalized_tag_names = [tag.strip().lower() for tag in tags if tag.strip()]

        if not normalized_tag_names:
            return []

        post_list = (
            select(PostOrm).options(
                selectinload(PostOrm.tags),
                joinedload(PostOrm.user)
            ).where(PostOrm.tags.any(func.lower(TagOrm.name).in_(normalized_tag_names))).order_by(PostOrm.id.asc())
        )

        return self.db.execute(post_list).scalars().all()

    def create_post(
            self,
            title: str,
            content: str,
            user: User,
            tags: List[dict],
            image_url: str,
            category_id: Optional[int]
    ) -> PostOrm:

        post = PostOrm(title=title, content=content, user=user, image_url=image_url, category_id=category_id)

        for tag in tags:
            names = tag['name'].split(',')
            for name in names:
                name = name.strip().lower()
                if not name:
                    continue
                tag_obj = self.tag_repository.ensure_tag(name)
                post.tags.append(tag_obj)

        self.db.add(post)
        self.db.flush()
        self.db.refresh(post)

        return post

    def update_post(self, post: PostOrm, update_obj: dict) -> PostOrm:
        for field, value in update_obj.items():
            setattr(post, field, value)

        return post

    def delete_post(self, post: PostOrm) -> None:
        self.db.delete(post)


def get_post_repository(db: Session = Depends(get_db),
                        tag_repository: TagRepository = Depends(get_tag_repository)) -> PostRepository:
    return PostRepository(db, tag_repository)
