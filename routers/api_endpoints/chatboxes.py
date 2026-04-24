### Core modules ###
from fastapi import (
    APIRouter,
    HTTPException,
    status
)
from sqlmodel import select


### Type hints ###
from ...cores.db import SessionDependency
from typing import (
    Any,
    Sequence
)
from ...types.tags import APITag
from pydantic.types import UUID7
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import ResponseValidationError


### Internal modules ###
from ...apis.table_models.chatboxes import Chatboxes
from ...apis.data_models.chatboxes import (
    # For validation (Data Model)
    ChatboxCreate,
    ChatboxUpdate
)
from ...types.api_responses.chatboxes import (
    # For client responses (Responses Model)
    ChatboxesPublicResponse,
    ChatboxCreateResponse,
    ChatboxPublicResponse,
    ChatboxUpdateResponse
)


chatboxes_v1_router: APIRouter = APIRouter(
    prefix="/api/v1/chatboxes",
    tags=[APITag.chatbox]
)


chatbox_post_description: str = """
## Extra information

This endpoint is strictly used for storing user-specific chat history for each
chatbox session. These data will be sent to our **Chatboxes** database table.

### Datetime format requirements

All datetime fields in this endpoint follow [**RFC 3339**](https://datatracker.ietf.org/doc/html/rfc3339)
format as strict mode enabled (Reference: [**Pydantic docs**](https://pydantic.dev/docs/validation/latest/concepts/strict_mode))

**1. Requirements**
- Must include `T` separator between date and time
- Must include timezone offset (`Z` or `±HH:MM`)

**2. Valid examples**
- `2024-12-24T21:20:00Z`        *(UTC)*
- `2024-12-24T16:20:00-05:00`   *(With offset)*
- `2024-12-24T21:20:00.123Z`    *(With milliseconds)*

**3. Invalid examples**
- `2024-12-24 21:20:00` *(Missing `T` separator)*
- `2024-12-24T21:20:00` *(Missing timezone)*
"""
chatbox_post_additional_responses: dict[int | str, dict[str, Any]] = {
    409: {
        "description": "Integrity Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "status": "409: Conflict",
                        "message": "string"
                    }
                }
            }
        }
    },
    500: {
        "description": "Type/Response Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "status": "500: Internal Server Error",
                        "message": "string"
                    }
                }
            }
        }
    }
}


@chatboxes_v1_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=ChatboxesPublicResponse
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


@chatboxes_v1_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=ChatboxCreateResponse,
    description=chatbox_post_description,
    responses=chatbox_post_additional_responses
)
async def create_chatbox_v1(
    chat_history: ChatboxCreate,
    session: SessionDependency
) -> Any:
    try:
        # NOTE:
        # `model_validate()` will keep non-standard Python types (e.g., custom
        # classes, library types, etc). Therefore, we've to dump those into valid
        # Python stdlib types so that it can be inserted/updated to the targeted
        # db table. SQLModel (or any ORMs, really) only handle incoming data that
        # have types match the convention for DB-specific system (with exception
        # on some custom types that are a part of the built-in Python modules).
        chatbox_validate_data:      Chatboxes       = Chatboxes.model_validate(obj=chat_history, strict=True)
        chatbox_compatible_data:    dict[str, Any]  = chatbox_validate_data.model_dump(mode="json", exclude_unset=True)
        chatbox_db:                 Chatboxes       = Chatboxes(**chatbox_compatible_data)

        session.add(instance=chatbox_db)
        session.commit()
        session.refresh(instance=chatbox_db)

        return {
            "success": True,
            "created": chatbox_db
        }

    except IntegrityError as psycopg_err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": "409 - Conflict",
                "message": f"{psycopg_err}"
            }
        )

    except TypeError as python_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "500 - Type Error",
                "message": f"{python_err}"
            }
        )

    except ResponseValidationError as fastapi_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "500 - Response Validation Error",
                "message": f"{fastapi_err}"
            }
        )


@chatboxes_v1_router.get(
    path="/{chatbox_session_id}",
    status_code=status.HTTP_200_OK,
    response_model=ChatboxPublicResponse
)
async def read_chatbox_v1(
    chatbox_session_id: UUID7,
    session: SessionDependency
) -> Any:
    chatbox_view: Chatboxes | None = session.get(entity=Chatboxes, ident=chatbox_session_id)

    if chatbox_view is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbox Session Not Found!"
        )
    else:
        return {
            "success": True,
            "result": chatbox_view
        }


@chatboxes_v1_router.patch(
    path="/{chatbox_session_id}",
    status_code=status.HTTP_200_OK,
    response_model=ChatboxUpdateResponse
)
async def update_chatbox_v1(
    chatbox_session_id: UUID7,
    chatbox_history: ChatboxUpdate,
    session: SessionDependency
) -> Any:
    chatbox_db: Chatboxes | None = session.get(entity=Chatboxes, ident=chatbox_session_id)

    if chatbox_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbox Not Found!"
        )
    else:
        chatbox_data: dict[str, Any] = chatbox_history.model_dump(mode="json", exclude_unset=True)
        chatbox_db.sqlmodel_update(obj=chatbox_data)

        session.add(instance=chatbox_db)
        session.commit()
        session.refresh(instance=chatbox_db)

        return {
            "success": True,
            "updated": chatbox_db
        }
