### Core modules ###
from fastapi import (
    APIRouter,
    HTTPException,
    status
)
from sqlalchemy.sql.expression import update
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
from sqlalchemy.sql.expression import Update


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
chatbox_update_description: str = """
## Extra information

This endpoint is used mainly for updating existing chat history in the
**Chatboxes** database table. The update behavior varies based on what data is
provided.

### Update Types

**1. Full Update (PUT semantics)**
- Replace the entire chatbox record
- All fields must be provided
- Missing fields will be set to NULL/default values
- Use when: Complete replacement of chatbox data

**2. Partial Update (PATCH semantics)**
- Update only specified fields
- Unspecified fields retain their current values
- Two subtypes:

    **2.1. Simple Column Data**
    - Scalar values (strings, integers, booleans)
    - Example: `{"name": "New Chat Name"}`
    - Direct column replacement

    **2.2. Complex Column Data (JSONB)**

    *2.2.1. Full JSON Replacement*
    - Replace entire JSON structure
    - Provide complete JSON object/array
    - Use when: Complete restructure of JSON data

    *2.2.2. Partial JSON Update (JSONB Path Operations)*
    - Update specific keys or array elements
    - Preserves untouched portions of JSON
    - Uses PostgreSQL `||` or `jsonb_set()` operations
    - Use when: Appending to arrays or modifying nested properties

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

### Update Operation Examples

```json
// Full update (all fields required)
{
    "name": "Updated Session",
    "details": {"theme": "dark", "messages": []},
    "updated_at": "2024-12-24T21:20:00Z"
}

// Partial update - simple fields only
{
    "name": "Renamed Session"
}

// Partial update - append to JSON array
{
    "details": {
        "_append": true,  // Special operator for array append
        "messages": [{"role": "user", "content": "Hello"}]
    }
}

// Partial update - modify specific JSON key
{
    "details": {
        "theme": "light"  // Only updates 'theme', preserves 'messages'
    }
}
"""
chatbox_additional_responses: dict[int | str, dict[str, Any]] = {
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
    responses=chatbox_additional_responses
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
    response_model=ChatboxUpdateResponse,
    description=chatbox_update_description,
    responses=chatbox_additional_responses
)
async def update_chatbox_v1(
    chatbox_session_id: UUID7,
    chat_history: ChatboxUpdate,
    session: SessionDependency
) -> Any:
    try:
        chatbox_db: Chatboxes | None = session.get(entity=Chatboxes, ident=chatbox_session_id)

        # Step 1:
        # Make sure chat session exists based on provided UUID
        if chatbox_db is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbox Not Found!"
            )

        # Step 2:
        # Chat session found, determine which kind of update are we going to perform:
        # 1. Full update
        # 2. Partial update
        #   2.1. Simple column data (e.g., name)
        #   2.2. Complex column data (e.g., details)
        #       2.2.1. Full JSON data (works like a full update)
        #       2.2.2. Partial JSON data (works like a partial update)
        # TODO:
        # I added ref here but this need to go to the right place:
        # 1. https://www.postgresql.org/docs/current/functions-json.html (`||` operator on JSOB column)
        # 2. https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.op (directly UPDATE statment with `||` operator)
        else:
            chatbox_data: dict[str, Any] = chat_history.model_dump(mode="json", exclude_unset=True)

            if ("details" in chatbox_data) and ("name" not in chatbox_data):
                #print("Chat history data update found!")
                chat_history_db_len: int = len(chatbox_db.details)

                if chat_history_db_len == 0:
                    #print("Empty chat history data found")
                    chatbox_db.details = chatbox_data["details"]
                    session.add(instance=chatbox_db)
                    session.commit()
                    session.refresh(instance=chatbox_db)
                    #print(f"Updated chat history data (empty case): {chatbox_db}")

                elif chat_history_db_len >= 1:
                    #print("Existing chat history data found")
                    chat_history_stmt: Update = (
                        update(table=Chatboxes)
                        .where(Chatboxes.id == chatbox_session_id)                              # pyright: ignore
                        .values(details=Chatboxes.details.op("||")(chatbox_data["details"]))    # pyright: ignore
                    )
                    session.exec(statement=chat_history_stmt)
                    session.commit()
                    session.refresh(instance=chatbox_db)
                    #print(f"Updated chat history data (exist case): {chatbox_db}")

                return {
                    "success": True,
                    "updated": chatbox_db
                }

            else:
                # This logic flow works for [1], [2.1] & [2.2.1]
                chatbox_db.sqlmodel_update(obj=chatbox_data)

                session.add(instance=chatbox_db)
                session.commit()
                session.refresh(instance=chatbox_db)

                return {
                    "success": True,
                    "updated": chatbox_db
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
