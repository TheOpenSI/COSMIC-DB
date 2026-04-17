### Core modules ###
from fastapi import (
    APIRouter,
    status
)
from sqlmodel import select


### Type hints ###
from ...cores.db import SessionDependency
from typing import Any, Sequence
from ...types.tags import APITag


### Internal modules ###
from ...apis.table_models.configurations import Configurations


configs_v1_router: APIRouter = APIRouter(
    prefix="/api/v1/configs",
    tags=[APITag.config]
)


@configs_v1_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def read_roles_v1(
    session: SessionDependency
) -> Any:
    configs_view: Sequence[Configurations] = session.exec(statement=select(Configurations)).all()
    total_configs: int = len(configs_view)

    if (total_configs == 0):
        return {
            "success": True,
            "count": total_configs, # 0
            "result": configs_view
        }
    else:
        return {
            "success": True,
            "count": total_configs, # all fetchable role data
            "result": configs_view
        }
