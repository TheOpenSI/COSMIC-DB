from sqlmodel import Field, SQLModel
from uuid import UUID


class EmissionsFilterParams(SQLModel):
    model_config = {"extra": "forbid"}

    user_id:     UUID | None = Field(default=None)
    emission_id: UUID | None = Field(default=None)


class EmissionsUserSummaryParams(SQLModel):
    model_config = {"extra": "forbid"}

    user_id: UUID


class EmissionsUserRollingParams(SQLModel):
    model_config = {"extra": "forbid"}

    user_id: UUID
    months: int = Field(default=3)