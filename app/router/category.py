from fastapi import APIRouter, Depends, status, HTTPException

from app.repository.category import get_category_repository
from app.schema.category import CategoryPublic, CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryPublic])
def list_categories(skip: int = 0, limit: int = 50, repository=Depends(get_category_repository)):
    return repository.list_many(skip=skip, limit=limit)


@router.post("", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, repository=Depends(get_category_repository)):
    exist = repository.get_by_slug(slug=data.slug)
    if exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")

    category = repository.create(name=data.name, slug=data.slug)

    repository.db.commit()
    repository.db.refresh(category)

    return category


@router.get("/{category_id}", response_model=CategoryPublic)
def get_category(category_id: int, repository=Depends(get_category_repository)):
    category = repository.get(category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category


@router.put("/{category_id}", response_model=CategoryPublic)
def update_category(category_id: int, data: CategoryUpdate, repository=Depends(get_category_repository)):
    category = repository.get(category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    updated = repository.update(category, data.model_dump(exclude_unset=True))

    repository.db.commit()
    repository.db.refresh(updated)

    return updated


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, repository=Depends(get_category_repository)):
    category = repository.get(category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    repository.delete(category)
    repository.db.commit()
