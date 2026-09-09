from math import ceil
from typing import Optional, Literal, List, Union, Annotated

from fastapi import APIRouter, Query, Depends, Path, HTTPException, status, UploadFile, File
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.security import require_user, require_editor, require_admin
from app.model import User
from app.repository.post import PostRepository, get_post_repository
from app.schema import PostPublic, PostSummary, PostCreate, PostUpdate
from app.schema.pagination import Pagination
from app.service.file_storage import save_uploaded_file

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=Pagination, response_description="List of posts with pagination")
def list_posts(
        title: Optional[str] = Query(
            default=None,
            description="Text to search posts by title",
            alias="search",
            min_length=3,
            max_length=50,
            pattern=r"^[\w\sáéíóúüñÁÉÍÓÚÜÑ-]+$"
        ),
        per_page: int = Query(
            default=10,
            ge=1,
            le=50,
            description="Maximum number of posts to return"
        ),
        page: int = Query(
            default=1,
            ge=1,
            description="Page number to retrieve"
        ),
        order_by: Literal["id", "title"] = Query(
            "id",
            description="Field to order the posts by"
        ),
        direction: Literal["asc", "desc"] = Query(
            "asc",
            description="Direction to order the posts"
        ),
        repository: PostRepository = Depends(get_post_repository)
):
    total, items = repository.search_posts(title, order_by, direction, page, per_page)

    total_pages = ceil(total / per_page) if total > 0 else 1
    current_page = 1 if total_pages == 0 else min(page, total_pages)

    return Pagination(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=current_page > 1,
        has_next=current_page < total_pages if total_pages > 0 else False,
        order_by=order_by,
        direction=direction,
        search=title,
        items=items
    )


@router.get("/by-tags", response_model=List[PostPublic], response_description="List of posts filtered by tags")
def get_posts_by_tags(
        tags: List[str] = Query(
            ...,
            description="List of tags to filter posts by. Example: ?tags=python&tags=fastapi",
            min_length=1,
            max_length=10
        ),
        repository: PostRepository = Depends(get_post_repository),
        _user: User = Depends(require_user)
):
    return repository.get_posts_by_tags(tags)


@router.get("/{post_id}", response_model=Union[PostPublic, PostSummary],
            response_description="Post details or summary")
def get_post(
        post_id: int = Path(
            ...,
            ge=1,
            title="Post ID",
            description="ID of the post to retrieve"
        ),
        include_content: bool | None = Query(
            default=True,
            description="Whether to include the content of the post"
        ),
        repository: PostRepository = Depends(get_post_repository),
        _user: User = Depends(require_user)
):
    post = repository.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return PostPublic.model_validate(post, from_attributes=True) if include_content else PostSummary.model_validate(
        post, from_attributes=True)


@router.post("", response_model=PostPublic, response_description="Created post details",
             status_code=status.HTTP_201_CREATED)
def create_post(
        post: Annotated[PostCreate, Depends(PostCreate.as_form)],
        repository: PostRepository = Depends(get_post_repository),
        image: Optional[UploadFile] = File(None),
        editor: User = Depends(require_editor)
):
    saved = None

    try:

        if image is not None:
            saved = save_uploaded_file(image)

        image_url = saved["url"] if saved else None

        new_post = repository.create_post(title=post.title, content=(post.content if post.content else ""),
                                          author=editor,
                                          tags=[tag.model_dump() for tag in post.tags], image_url=image_url)
        repository.db.commit()
        repository.db.refresh(new_post)
        return new_post
    except IntegrityError:
        repository.db.rollback()
        raise HTTPException(status_code=409, detail=f"Post with title {post.title} already exists")
    except SQLAlchemyError:
        repository.db.rollback()
        raise HTTPException(status_code=500, detail="Error while creating post")


@router.put("/{post_id}", response_model=PostPublic, response_description="Updated post details",
            response_model_exclude_none=True)
def update_post(post_id: int, updated_data: PostUpdate, repository: PostRepository = Depends(get_post_repository),
                _editor: User = Depends(require_editor)):
    post = repository.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    try:
        post_updated = repository.update_post(post=post, update_obj=updated_data.model_dump(exclude_unset=True))
        repository.db.commit()
        repository.db.refresh(post_updated)
        return post_updated
    except SQLAlchemyError:
        repository.db.rollback()
        raise HTTPException(status_code=500, detail="Error while updating post")


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT,
               response_description="Post deleted successfully")
def delete_post(post_id: int, repository: PostRepository = Depends(get_post_repository),
                _admin: User = Depends(require_admin)):
    post_db = repository.get_post(post_id)

    if not post_db:
        raise HTTPException(status_code=404, detail="Post not found")

    try:
        repository.delete_post(post=post_db)
        repository.db.commit()
    except SQLAlchemyError:
        repository.db.rollback()
        raise HTTPException(status_code=500, detail="Error while deleting post")
