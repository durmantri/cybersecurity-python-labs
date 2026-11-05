from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


#  Базовий клас конфігурації для заборони невідомих полів
class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


# Валідація рядків
def validate_non_empty_string(v: str) -> str:
    if not isinstance(v, str):
        raise TypeError("Значення має бути рядком")
    cleaned = v.strip()
    if not cleaned:
        raise ValueError("Рядок не може бути порожнім або складатися лише з пробілів")
    return cleaned


# Моделі категорій


class CategoryCreate(StrictModel):
    name: str = Field(..., min_length=2, max_length=50, description="Назва категорії")

    @field_validator("name", mode="before")
    @classmethod
    def check_name(cls, v: str) -> str:
        return validate_non_empty_string(v)


class CategoryRead(StrictModel):
    id: int = Field(..., gt=0, description="ID категорії")
    name: str


#  Моделі записування


class RecordCreate(StrictModel):
    code: str = Field(
        ..., min_length=3, max_length=40, description="Унікальний код запису"
    )
    title: str = Field(
        ..., min_length=3, max_length=120, description="Назва події/спостереження"
    )
    category_id: int = Field(..., gt=0, description="ID існуючої категорії")
    value: int = Field(..., ge=0, description="Кількість подій (ціле число >= 0)")
    status: Literal["new", "in_progress", "done"] = Field(
        ..., description="Статус виконання"
    )

    @field_validator("code", "title", mode="before")
    @classmethod
    def check_strings(cls, v: str) -> str:
        return validate_non_empty_string(v)


class RecordReplace(RecordCreate):
    """
    Модель для повного оновлення запису (PUT).
    Успадковує RecordCreate: усі поля обов'язкові, клієнт не передає id.
    """


class RecordRead(StrictModel):
    """
    Модель для читання запису.
    Повертає id та category_name разом з усіма змінюваними полями.
    """

    id: int = Field(..., gt=0)
    code: str
    title: str
    category_id: int = Field(..., gt=0)
    category_name: str = Field(..., description="Назва категорії з'єднана через JOIN")
    value: int = Field(..., ge=0)
    status: Literal["new", "in_progress", "done"]


class RecordsBulkCreate(StrictModel):
    """
    Модель для пакетного додавання записів.
    Кількість елементів пакета: від 1 до 100.
    """

    records: list[RecordCreate] = Field(
        ..., min_length=1, max_length=100, description="Список записів від 1 до 100"
    )
