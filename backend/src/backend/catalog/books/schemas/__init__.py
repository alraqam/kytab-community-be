from typing import TypeVar, Generic

from pydantic import BaseModel, Field, computed_field

T = TypeVar("T")


class PageRequest(BaseModel):
    """Pagination request parameters with page number and page size."""

    page: int = Field(ge=1, default=1)
    size: int = Field(ge=1, default=50)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size

class PageResult(BaseModel, Generic[T]):
    """Generic paginated response with items, totals, and navigation flags."""

    items: list[T]
    page: int
    size: int
    total_items: int

    @computed_field
    @property
    def total_pages(self) -> int:
        if self.total_items == 0:
            return 0
        return (self.total_items + self.size - 1) // self.size

    @computed_field
    @property
    def has_next_page(self) -> bool:
        return self.page < self.total_pages

    @computed_field
    @property
    def has_prev_page(self) -> bool:
        return self.page > 1

    @classmethod
    def empty(cls, page: int = 1, size: int = 50):
        return cls(items=[], page=page, size=size, total_items=0)
