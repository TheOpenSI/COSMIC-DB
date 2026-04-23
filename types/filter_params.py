### Core modules ###
from sqlmodel import Field, SQLModel


### Type hints ###


### Internal modules ###


class ServiceFilterParams(SQLModel):
    # NOTE:
    # There wasn't any clear explanation on FastAPI docs when they use this in
    # one of the examples. Take a look at linked Pydantic docs here for more
    # detail:
    # https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict.extra
    # https://fastapi.tiangolo.com/tutorial/query-param-models/#forbid-extra-query-parameters 
    model_config = {"extra": "forbid"}

    active: bool | None = Field(default=None)
