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
from ...apis.table_models.statistics import Statistics


stats_v1_router: APIRouter = APIRouter(
    prefix="/api/v1/stats",
    tags=[APITag.stat]
)


@stats_v1_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def read_stats_v1(
    session: SessionDependency
) -> Any:
    stats_view: Sequence[Statistics] = session.exec(statement=select(Statistics)).all()
    total_stats: int = len(stats_view)

    if (total_stats == 0):
        return {
            "success": True,
            "count": total_stats, # 0
            "result": stats_view
        }
    else:
        return {
            "success": True,
            "count": total_stats, # all fetchable stats data
            "result": stats_view
        }
