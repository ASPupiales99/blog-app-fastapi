from slugify import slugify as _slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model import PostOrm


def slugify_base(text: str) -> str:
    slug = _slugify(text, lowercase=True, separator="-")
    return slug or "post"


def ensure_unique_slug(db: Session, base_text: str) -> str:
    base = slugify_base(base_text)
    exists = db.execute(
        select(PostOrm).where(PostOrm.slug.like(f"{base}%"))
    ).scalars().all()

    if base not in exists:
        return base

    i = 2
    candidate = f"{base}-{i}"
    while candidate in exists:
        i += 1
        candidate = f"{base}-{i}"

    return candidate