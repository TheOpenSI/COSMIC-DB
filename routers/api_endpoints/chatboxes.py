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
    ChatboxUpdateResponse,
    ChatboxDeleteResponse
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

**1. Full Update**
- Replace the entire chatbox record
- All fields must be provided

**2. Partial Update**
- Update only specified fields
- Unspecified fields is safely ignored thanks to Pydantic validation
- We got 2 main sub-types to aware about:

    **2.1. Simple Column Data**
    - Scalar values (strings, integers, booleans)
    - Example: `{"name": "New Chat Name"}`

    **2.2. Complex Column Data (JSONB)**
    - For our usecase, it'll be used to append to existing data only
    - Uses PostgreSQL `||` operator to efficiently join complex JSONB data

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
**NOTE:
We wrote this in YAML format for better readability. Please convert to JSON
format (if needed).**


```yaml
// Full update (all fields required)
user_id: "019dc32b-2f4a-7931-ab92-f6d6bf9e9ba4",
name: "<chat session title>",
details:
    - user_role: "<user role>",
      user_query: "<user query>",
      query_create_on: "2026-04-25T05:44:23.647Z",
      llm_role: "<llm role>",
      llm_response: "<llm response>",
      response_create_on: "2026-04-25T05:44:23.647Z"

    # Specify more here


// Partial update (simple fields only)
name: "<chat session title>"


// Partial update (complex fields only)
details:
    - user_role: "<user role>",
      user_query: "<user query>",
      query_create_on: "2026-04-25T05:44:23.647Z",
      llm_role: "<llm role>",
      llm_response: "<llm response>",
      response_create_on: "2026-04-25T05:44:23.647Z"

    # Specify more here
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

            match chatbox_data:
                #==============================================================#
                #                           Case 1:                            #
                #                           Full update                        #
                #==============================================================#
                case {
                    "user_id": user_id,
                    "name": user_name,
                    "details": user_chat_history
                }:
                    #print("Case 1: Full update - replace everything")
                    chatbox_prep_data: dict[str, Any] = {}

                    if (str(chatbox_db.user_id) != user_id):
                        chatbox_prep_data["user_id"] = user_id

                    else:
                        # Incoming data matched stored data, skipping.
                        pass

                    if (str(chatbox_db.name) != user_name):
                        chatbox_prep_data["name"] = user_name

                    else:
                        # Incoming data matched stored data, skipping.
                        pass

                    if (chatbox_db.details != user_chat_history):
                        if any(new_chat_history not in chatbox_db.details for new_chat_history in user_chat_history):
                            # NOTE: only for type-hint purposes, no actual effect to the logic
                            new_chat_history: dict[str, Any]
                            chatbox_prep_data["details"] = Chatboxes.details.op("||")(user_chat_history) # pyright: ignore

                        else:
                            # Incoming JSON data matched stored JSON data, skipping.
                            pass

                    else:
                        # Incoming data matched stored data, skipping.
                        # NOTE:
                        # This edge case only work when chat history size is
                        # exactly one
                        pass

                    if chatbox_prep_data:
                        chatbox_stmt: Update = (
                            update(table=Chatboxes)
                            .where(Chatboxes.id == chatbox_session_id)  # pyright: ignore
                            .values(**chatbox_prep_data)                # pyright: ignore
                            .returning(Chatboxes)
                        )
                        session.exec(statement=chatbox_stmt)
                        session.commit()

                    else:
                        # Incoming data matched stored data, skipping.
                        # NOTE:
                        # This edge case only work when all the check above
                        # is false
                        pass


                #==============================================================#
                #                           Case 2A:                           #
                #       Partial update, simple data only (either key provided) #
                #==============================================================#
                case {"user_id": user_id}           \
                if   ("name" not in chatbox_data)   \
                and  ("details" not in chatbox_data):
                    #print("Case 2A: Partial update - simple data only (update new 'user_id' basic record)")
                    if str(chatbox_db.user_id) == user_id:
                        # Do nothing as the data matched
                        pass

                    else:
                        chatbox_db.sqlmodel_update(obj=chatbox_data)

                        session.add(instance=chatbox_db)
                        session.commit()
                        session.refresh(instance=chatbox_db)


                #==============================================================#
                #                           Case 2B:                           #
                #       Partial update, simple data only (either key provided) #
                #==============================================================#
                case {"name": user_name}                \
                if   ("user_id" not in chatbox_data)    \
                and  ("details" not in chatbox_data):
                    #print("Case 2B: Partial update - simple data only (update new 'name' basic record)")
                    if str(chatbox_db.name) == user_name:
                        # Do nothing as the data matched
                        pass

                    else:
                        chatbox_db.sqlmodel_update(obj=chatbox_data)

                        session.add(instance=chatbox_db)
                        session.commit()
                        session.refresh(instance=chatbox_db)


                #==============================================================#
                #                           Case 2C:                           #
                #       Partial update, simple data only (all key provided)    #
                #==============================================================#
                case {"user_id": user_id, "name": user_name} \
                if "details" not in chatbox_data:
                    #print("Case 2C: Partial update - simple data only (update new basic record)")
                    if  (str(chatbox_db.user_id) == user_id) \
                    and (str(chatbox_db.name) == user_name):
                        # Do nothing as the data matched
                        pass

                    else:
                        chatbox_db.sqlmodel_update(obj=chatbox_data)

                        session.add(instance=chatbox_db)
                        session.commit()
                        session.refresh(instance=chatbox_db)


                #==============================================================#
                #                           Case 3:                            #
                #       Partial update, complex data only (various scenarios)  #
                #==============================================================#
                case {"details": user_chat_history}     \
                if   ("user_id" not in chatbox_data)    \
                and  ("name" not in chatbox_data):
                    # WARNING:
                    # Later on when we eventually added the ability for user to
                    # edit convo pairs, this check would need to be update as
                    # well as the db schema.

                    #print("Case 3: Partial update - complex data only (various scenarios)")
                    if len(chatbox_db.details) >= 0:
                        chatbox_stmt: Update = (
                            update(table=Chatboxes)
                            .where(Chatboxes.id == chatbox_session_id)                              # pyright: ignore
                            .values(details=Chatboxes.details.op("||")(chatbox_data["details"]))    # pyright: ignore
                            .returning(Chatboxes)
                        )
                        session.exec(statement=chatbox_stmt)
                        session.commit()

                    else:
                        pass


                #==============================================================#
                #                           Case ???:                          #
                #       Unknown update, fallback for invalid case matching     #
                #==============================================================#
                case _:
                    #print ("Case ???: Unknown update - no matching case")
                    pass

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


@chatboxes_v1_router.delete(
    path="/{chatbox_session_id}",
    status_code=status.HTTP_200_OK,
    response_model=ChatboxDeleteResponse
)
async def delete_chatbox_v1(
    chatbox_session_id: UUID7,
    session: SessionDependency
) -> Any:
    chatbox_gone: Chatboxes | None = session.get(entity=Chatboxes, ident=chatbox_session_id)

    if chatbox_gone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbox Not Found!"
        )
    else:
        session.delete(instance=chatbox_gone)
        session.commit()

        return {
            "success": True,
            "deleted": chatbox_gone
        }
