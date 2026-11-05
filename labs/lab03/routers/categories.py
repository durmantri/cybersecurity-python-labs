import sqlite3

from fastapi import APIRouter, HTTPException, status

from labs.lab03 import repository
from labs.lab03.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "",
    response_model=list[CategoryRead],
    status_code=status.HTTP_200_OK,
    summary="Отримати список категорій",
)
def get_categories():
    """Повертає список усіх доступних категорій."""
    return repository.get_categories()


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити нову категорію",
)
def create_category(body: CategoryCreate):
    """Створює нову категорію."""
    try:
        cat_id = repository.create_category(body.name)
        return {"id": cat_id, "name": body.name}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Помилка створення категорії",
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити порожню категорію",
)
def delete_category(category_id: int):
    """
    Видаляє категорію за ID.
    Якщо до категорії прив'язані записи, база даних заблокує видалення.
    """
    try:
        success = repository.delete_empty_category(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категорію з ID {category_id} не знайдено.",
            )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Неможливо видалити категорію, оскільки вона містить пов'язані записи",
        )
