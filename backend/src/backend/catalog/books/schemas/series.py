from pydantic import BaseModel, ConfigDict, Field


class CreateSeries(BaseModel):
    """Request payload for creating a new series."""

    name: str = Field(max_length=512)

class UpdateSeries(BaseModel):
    """Request payload for updating series details."""

    name: str | None = Field(default=None, max_length=512)

class GetSeries(BaseModel):
    """Series data returned in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class AddWorkToSeries(BaseModel):
    """Request payload for linking a work to a series."""

    work_id: int
    series_id: int
    sequence_number: int | None = None
