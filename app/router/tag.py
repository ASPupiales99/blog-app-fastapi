from fastapi import APIRouter, status, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import require_editor, require_admin, require_user
from app.model import User
from app.repository.tag import get_tag_repository
from app.schema.tag import TagPublic, TagCreate, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("", response_model=TagPublic, response_description="Tag created", status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, repository=Depends(get_tag_repository), _editor: User = Depends(require_editor)):
    try:
        new_tag = repository.create_tag(name=tag.name)
        repository.db.commit()
        repository.db.refresh(new_tag)

        return new_tag

    except SQLAlchemyError:
        repository.db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating tag")


@router.get("", response_model=dict)
def list_tags(
        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=1, le=100),
        order_by: str = Query("id", pattern="^(id|name)$"),
        direction: str = Query("asc", pattern="^(asc|desc)$"),
        search: str | None = Query(None),
        repository=Depends(get_tag_repository),
):
    return repository.search_tags(
        page=page,
        per_page=per_page,
        order_by=order_by,
        direction=direction,
        search=search
    )


@router.get("/popular")
def get_popular_tag(repository=Depends(get_tag_repository), _user: User = Depends(require_user)):
    row = repository.get_most_popular_tag()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tags in use not found")

    return row


@router.put("/{tag_id}", response_model=TagPublic, response_description="Tag updated", status_code=status.HTTP_200_OK)
def update_tag(tag_id: int, tag_update: TagUpdate, repository=Depends(get_tag_repository),
               _editor: User = Depends(require_editor)):
    updated_tag = repository.update_tag(tag_id, name=tag_update.name)

    if not updated_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    repository.db.commit()

    return TagPublic.model_validate(updated_tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, repository=Depends(get_tag_repository), _admin: User = Depends(require_admin)):
    deleted_tag = repository.delete_tag(tag_id)

    if not deleted_tag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting tag")

    repository.db.commit()
