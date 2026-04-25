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
from ...apis.table_models.chatboxes import Chatboxes


chatboxes_v1_router: APIRouter = APIRouter(
    prefix="/api/v1/chatboxes",
    tags=[APITag.chatbox]
)


@chatboxes_v1_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def read_chatboxes_v1(
    session: SessionDependency
) -> Any:
    chatboxes_view: Sequence[Chatboxes] = session.exec(statement=select(Chatboxes)).all()
    total_chatboxes: int = len(chatboxes_view)

    if (total_chatboxes == 0):
        return {
            "success": True,
            "count": total_chatboxes, # 0
            "result": chatboxes_view
        }
    else:
        return {
            "success": True,
            "count": total_chatboxes, # all fetchable chatboxes data
            "result": chatboxes_view
        }
