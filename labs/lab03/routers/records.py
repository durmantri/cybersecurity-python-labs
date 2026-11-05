import sqlite3
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from labs.lab03 import repository
from labs.lab03.schemas import (
    RecordCreate,
    RecordRead,
    RecordReplace,
    RecordsBulkCreate,
)

router = APIRouter(prefix="/records", tags=["Records"])


@router.get(
    "",
    response_model=list[RecordRead],
    status_code=status.HTTP_200_OK,
    summary="Отримати список записів",
    description=("Повертає список подій з можливістю фільтрації."),
)
def get_records(
    category_id: int | None = Query(None, gt=0, description="Фільтр за ID категорії"),
    status_filter: Literal["new", "in_progress", "done"] | None = Query(
        None, alias="status", description="Фільтр за статусом"
    ),
    min_value: int | None = Query(
        None, ge=0, description="Мінімальне значення value (>= 0)"
    ),
    q: str | None = Query(
        None, min_length=1, description="Пошук підрядка в назві (title)"
    ),
    limit: int = Query(
        20, ge=1, le=100, description="Кількість записів на сторінку (від 1 до 100)"
    ),
    offset: int = Query(0, ge=0, description="Кількість пропущених записів "),
):
    """
    Ендпоінт викликає функцію репозиторію для вибірки даних з бази даних
    з урахуванням усіх переданих параметрів та JOIN-об'єднання з категоріями.
    """
    records = repository.get_records(
        category_id=category_id,
        status=status_filter,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )
    return records


@router.post(
    "",
    response_model=RecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити новий запис",
)
def create_record(body: RecordCreate):
    """Створює новий запис події поштової безпеки."""
    try:
        created = repository.create_record(
            code=body.code,
            title=body.title,
            category_id=body.category_id,
            value=body.value,
            status=body.status,
        )
        return created
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Помилка створення запису (можливо, дублікат коду або невідома категорія)",
        )


@router.get(
    "/{record_id}",
    response_model=RecordRead,
    status_code=status.HTTP_200_OK,
    summary="Отримати запис за ID",
)
def get_record(record_id: int):
    """Повертає один запис разом із назвою категорії за його ID."""
    record = repository.get_record_by_id(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запис із ID {record_id} не знайдено.",
        )
    return record


@router.put(
    "/{record_id}",
    response_model=RecordRead,
    status_code=status.HTTP_200_OK,
    summary="Оновлення запису",
)
def update_record(record_id: int, body: RecordReplace):
    """Оновлює всі змінювані поля запису за його ID."""
    updated = repository.update_record(
        record_id=record_id,
        code=body.code,
        title=body.title,
        category_id=body.category_id,
        value=body.value,
        status=body.status,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запис із ID {record_id} для оновлення не знайдено.",
        )
    return updated


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити запис за ID",
)
def delete_record(record_id: int):
    """Видаляє запис за його ID."""
    success = repository.delete_record(record_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запис із ID {record_id} для видалення не знайдено.",
        )


@router.post(
    "/bulk",
    response_model=list[RecordRead],
    status_code=status.HTTP_201_CREATED,
    summary="Пакетне додавання записів",
    description="Додає від 1 до 100 записів в одній транзакції.",
)
def create_records_bulk(body: RecordsBulkCreate):
    codes = [item.code for item in body.records]
    if len(codes) != len(set(codes)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пакет містить записи з однаковими кодами.",
        )

    data_dicts = [item.model_dump() for item in body.records]

    try:
        created_records = repository.create_records_bulk(data_dicts)
        return created_records

    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()

        # Обробка неіснуючої категорії
        if "foreign key constraint failed" in err_msg or "category_id" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Одна або кілька вказаних категорій не існують у базі даних (транзакцію скасовано).",
            )

        # Обробка дублікатів
        elif "unique constraint failed" in err_msg or "records.code" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Один із кодів запису вже існує в базі даних (транзакцію скасовано).",
            )

        # Порушення цілісності даних
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Порушення цілісності даних (транзакцію скасовано): {e}",
            )
