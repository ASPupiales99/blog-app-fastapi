from math import ceil
from typing import Optional, Tuple, List

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload, joinedload

from app.core.db import get_db
from app.model import PostOrm, TagOrm
from app.repository import AuthorRepository, TagRepository
from app.repository.author import get_author_repository
from app.repository.tag import get_tag_repository


class PostRepository:
    def __init__(self, db: Session, author_repository: AuthorRepository, tag_repository: TagRepository):
        self.db = db
        self.author_repository = author_repository
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
                joinedload(PostOrm.author)
            ).where(PostOrm.tags.any(func.lower(TagOrm.name).in_(normalized_tag_names))).order_by(PostOrm.id.asc())
        )

        return self.db.execute(post_list).scalars().all()

    def create_post(self, title: str, content: str, author: Optional[dict], tags: List[dict]) -> PostOrm:
        author_obj = None
        if author:
            author_obj = self.author_repository.ensure_author(author['username'], author['email'])

        post = PostOrm(title=title, content=content, author=author_obj)

        for tag in tags:
            tag_obj = self.tag_repository.ensure_tag(tag['name'])
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
                        author_repository: AuthorRepository = Depends(get_author_repository),
                        tag_repository: TagRepository = Depends(get_tag_repository)) -> PostRepository:
    return PostRepository(db, author_repository, tag_repository)
