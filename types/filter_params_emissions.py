from sqlmodel import Field,SQLModel
from uuid import UUID

### Internal modules ###


class EmissionsFilterParams(SQLModel):
    model_config = {"extra": "forbid"}

    user_id:     UUID | None = Field(default=None)
    chat_id:     UUID | None = Field(default=None)
    emission_id: UUID | None = Field(default=None)