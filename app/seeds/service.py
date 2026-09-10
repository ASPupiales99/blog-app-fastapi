from contextlib import contextmanager
from typing import Optional

from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import sessionLocal
from app.model import User, CategoryOrm, TagOrm
from app.seeds.data.categories import CATEGORIES
from app.seeds.data.tags import TAGS
from app.seeds.data.users import USERS


def hash_password(password: str) -> str:
    return PasswordHash.recommended().hash(password)


@contextmanager
def atomic(db: Session):
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise


def _user_by_email(db: Session, email: str) -> Optional[User]:
    return db.execute(
        select(User).where(User.email == email)
    ).scalars().first()


def _category_slug(db: Session, slug: str) -> Optional[CategoryOrm]:
    return db.execute(
        select(CategoryOrm).where(CategoryOrm.slug == slug)
    ).scalars().first()


def _tag_by_name(db: Session, name: str) -> Optional[TagOrm]:
    return db.execute(
        select(TagOrm).where(TagOrm.name == name)
    ).scalars().first()


def seed_users(db: Session) -> None:
    with atomic(db):
        for data in USERS:
            obj = _user_by_email(db, data['email'])
            if obj:
                changed = False

                if obj.full_name != data['full_name']:
                    obj.full_name = data['full_name']
                    changed = True

                if data['password']:
                    obj.password = hash_password(data['password'])
                    changed = True

                if data['role']:
                    obj.role = data['role']
                    changed = True

                if changed:
                    db.add(obj)
            else:
                db.add(User(
                    email=data['email'],
                    full_name=data['full_name'],
                    role=data['role'],
                    password=hash_password(data['password'])
                ))


def seed_categories(db: Session) -> None:
    with atomic(db):
        for data in CATEGORIES:
            obj = _category_slug(db, data['slug'])
            if obj:
                if obj.name != data['name']:
                    obj.name = data['name']
                    db.add(obj)
            else:
                db.add(CategoryOrm(
                    name=data['name'],
                    slug=data['slug'],
                ))


def seed_tags(db: Session) -> None:
    with atomic(db):
        for data in TAGS:
            obj = _tag_by_name(db, data['name'])
            if obj:
                if obj.name != data['name']:
                    obj.name = data['name']
                    db.add(obj)
            else:
                db.add(TagOrm(
                    name=data['name'],
                ))


def run_all() -> None:
    with sessionLocal() as db:
        seed_users(db)
        seed_categories(db)
        seed_tags(db)


def run_users() -> None:
    with sessionLocal() as db:
        seed_users(db)


def run_categories() -> None:
    with sessionLocal() as db:
        seed_categories(db)


def run_tags() -> None:
    with sessionLocal() as db:
        seed_tags(db)
