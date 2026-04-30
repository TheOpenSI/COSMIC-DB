### Core modules ###
from datetime import datetime
from uuid import (
    UUID,
    SafeUUID
)
from fastapi import (
    APIRouter,
    HTTPException,
    status
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.expression import update
from sqlalchemy.sql.functions import func
from sqlmodel import select
from httpx import (
    AsyncClient,
    ConnectError,
    ConnectTimeout,
    Response
)


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
from sqlalchemy.sql.elements import BinaryExpression, ColumnElement


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


chatbox_additional_responses: dict[int | str, dict[str, Any]] = {
    400: {
        "description": "Value Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "status": "400: Bad Request",
                        "message": "string"
                    }
                }
            }
        }
    },
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
    responses=chatbox_additional_responses
)
async def update_chatbox_v1(
    chatbox_session_id: UUID7,
    chatbox: ChatboxUpdate,
    session: SessionDependency
) -> Any:
    try:
        chatbox_db: Chatboxes | None = session.get(entity=Chatboxes, ident=chatbox_session_id)

        if chatbox_db is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbox Not Found!"
            )

        else:
            chatbox_data: dict[str, Any] = chatbox.model_dump(mode="json", exclude_unset=True)

            # Case 1: full data updates
            if all(key in chatbox_data for key in ("user_id", "name", "details")):
                chatbox_user_id:    str                     = chatbox_data["user_id"]
                chatbox_name:       str                     = chatbox_data["name"]
                chatbox_details:    list[dict[str, Any]]    = chatbox_data["details"]

                # NOTE:
                # It's much more safe and accurate to compare UUID value in its
                # original form (UUID Object). The compiler will now understand
                # that we're matching them in chronological logic instead.
                if UUID(
                    hex=chatbox_user_id,
                    version=7,
                    is_safe=SafeUUID.safe
                ) != chatbox_db.user_id:
                    # We CANNOT change specified chatbox ownership
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "status": "400 - Bad Request",
                            "message": "{trig:s}: {cond:s}".format(
                                trig="Chatbox update forbidden",
                                cond=f"Chatbox ownership (user ID) cannot be updated: {chatbox_db.user_id} --> {chatbox_user_id}"
                            )
                        }
                    )

                else:
                    chatbox_db.name     = chatbox_name
                    chatbox_db.details  = chatbox_details # pyright: ignore

                    session.add(instance=chatbox_db)
                    session.commit()
                    session.refresh(instance=chatbox_db)

            # Case 2: partial data updates
            else:
                if "user_id" in chatbox_data:
                    chatbox_user_id: str = chatbox_data["user_id"]
                    # NOTE:
                    # It's much more safe and accurate to compare UUID value in its
                    # original form (UUID Object). The compiler will now understand
                    # that we're matching them in chronological logic instead.
                    if UUID(
                        hex=chatbox_user_id,
                        version=7,
                        is_safe=SafeUUID.safe
                    ) != chatbox_db.user_id:
                        # We CANNOT change specified chatbox ownership
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail={
                                "status": "400 - Bad Request",
                                "message": "{trig:s}: {cond:s}".format(
                                    trig="Chatbox update forbidden",
                                    cond=f"Chatbox ownership (user ID) cannot be updated: {chatbox_db.user_id} --> {chatbox_user_id}"
                                )
                            }
                        )

                    else:
                        # Case 2a: partial data updates (chatbox name)
                        if "name" in chatbox_data:
                            chatbox_name: str = chatbox_data["name"]

                            if chatbox_name == chatbox_db.name:
                                # Incoming data matched stored data so no need to
                                # waste disk I/O for running update on nothing
                                pass

                            else:
                                # NOTE:
                                # We didn't use `sqlmodel_update()` method here since
                                # specified chatbox ownership cannot be modified, but
                                # we still have to provide the `user_id` data, which
                                # this method will execute surgical update on BOTH
                                # `user_id` & `name` data.
                                chatbox_db.name = chatbox_name # pyright: ignore

                                session.add(instance=chatbox_db)
                                session.commit()
                                session.refresh(instance=chatbox_db)

                        else:
                            # Update other data than chatbox name
                            pass

                        # Case 2b: partial data updates (chatbox details)
                        if "details" in chatbox_data:
                            # NOTE:
                            # Endpoints calling from the same container doesn't need
                            # to know the container service name
                            roles_endpoint: str = "http://localhost:8000/api/v1/roles/"
                            roles_timeout:  float = 10.0

                            async with AsyncClient(
                                base_url=roles_endpoint,
                                timeout=roles_timeout
                            ) as client:
                                try:
                                    roles_response: Response = await client.get(url="/")
                                    roles_data: list[dict[str, Any]] = roles_response.json()["result"]
                                    roles_name: list[str] = [
                                        value
                                        for role_data in roles_data
                                        for (key, value) in role_data.items()
                                        if "name" in key
                                    ]

                                    # Sub-case 2b - Scenario 1:
                                    # Continuously adding chat convo to current
                                    # chat history data
                                    if (len(chatbox_data["details"]) < len(chatbox_db.details)) \
                                    or (len(chatbox_data["details"]) > len(chatbox_db.details)):
                                        new_chat_history: list[dict[ColumnElement, BinaryExpression[Any]]] = [] # pyright: ignore
                                        new_chat_convo: BinaryExpression[Any] = Chatboxes.details # pyright: ignore

                                        for (
                                            chat_history_idx,
                                            chat_history
                                        ) in enumerate(
                                            iterable=chatbox_data["details"],
                                            start=0
                                        ):
                                            chat_user_role: str = chat_history["user_role"]
                                            chat_llm_role:  str = chat_history["llm_role"]

                                            if  (chat_user_role.capitalize() in roles_name) \
                                            and (chat_llm_role.capitalize() in roles_name):
                                                # Valid role name, good to process
                                                pass

                                        new_chat_history.append( # pyright: ignore
                                            {
                                                new_chat_convo: (
                                                    func.cast(new_chat_convo, JSONB)
                                                ).op("||")(
                                                    func.cast(chatbox_data["details"], JSONB)
                                                )
                                            }
                                        )

                                    # Sub-case 2b - Scenario 2:
                                    # Surgical updates (1 or many) to each
                                    # current chat history data
                                    else:
                                        new_chat_history: dict[ColumnElement, Any] = {}

                                        for (
                                            chat_history_idx,
                                            chat_history
                                        ) in enumerate(
                                            iterable=chatbox_data["details"],
                                            start=0
                                        ):
                                            # Sub-case 2b - Scenario 3.1:
                                            # User role surgical updates
                                            chat_user_role: str = chat_history["user_role"]

                                            if  (chat_user_role.capitalize() in roles_name) \
                                            and (chat_user_role != chatbox_db.details[chat_history_idx]["user_role"]): # pyright: ignore
                                                # To match role name format from called endpoint
                                                new_chat_history[Chatboxes.details[chat_history_idx]["user_role"]] = chat_user_role.capitalize() # pyright: ignore


                                            # Sub-case 2b - Scenario 3.2:
                                            # LLM role surgical updates
                                            chat_llm_role: str = chat_history["llm_role"]

                                            if  (chat_llm_role.capitalize() in roles_name) \
                                            and (chat_llm_role != chatbox_db.details[chat_history_idx]["llm_role"]): # pyright: ignore
                                                # To match role name format from called endpoint
                                                new_chat_history[Chatboxes.details[chat_history_idx]["llm_role"]] = chat_llm_role.capitalize() # pyright: ignore


                                            # Sub-case 2b - Scenario 3.3:
                                            # User query updates, which its timestamp
                                            # must be updated as well to reflect accurate
                                            # new changes
                                            chat_user_query:        str = chat_history["user_query"]
                                            chat_user_timestamp:    str = chat_history["query_create_on"]

                                            if chat_user_query != chatbox_db.details[chat_history_idx]["user_query"]: # pyright: ignore
                                                new_chat_history[Chatboxes.details[chat_history_idx]["user_query"]] = chat_user_query # pyright: ignore

                                            if (
                                                # NOTE:
                                                # It's much more safe and accurate to
                                                # compare timestamp value in its original
                                                # form (datetime Object). The compiler
                                                # will now understand that we're matching
                                                # them in chronological logic instead.
                                                datetime.fromisoformat(chat_user_timestamp) \
                                                !=
                                                datetime.fromisoformat(chatbox_db.details[chat_history_idx]["query_create_on"]) # pyright: ignore
                                            ):
                                                new_chat_history[Chatboxes.details[chat_history_idx]["query_create_on"]] = chat_user_timestamp # pyright: ignore


                                            # Sub-case 2b - Scenario 3.4:
                                            # LLM response updates, which its timestamp
                                            # must be updated as well to reflect accurate
                                            # new changes
                                            chat_llm_response:      str = chat_history["llm_response"]
                                            chat_llm_timestamp:     str = chat_history["response_create_on"]

                                            if chat_llm_response != chatbox_db.details[chat_history_idx]["llm_response"]: # pyright: ignore
                                                new_chat_history[Chatboxes.details[chat_history_idx]["llm_response"]] = chat_llm_response # pyright: ignore

                                            if (
                                                # NOTE:
                                                # It's much more safe and accurate to
                                                # compare timestamp value in its original
                                                # form (datetime Object). The compiler
                                                # will now understand that we're matching
                                                # them in chronological logic instead.
                                                datetime.fromisoformat(chat_llm_timestamp) \
                                                !=
                                                datetime.fromisoformat(chatbox_db.details[chat_history_idx]["response_create_on"]) # pyright: ignore
                                            ):
                                                new_chat_history[Chatboxes.details[chat_history_idx]["response_create_on"]] = chat_llm_timestamp # pyright: ignore


                                    #TODO: some sort of `verbose` argument toggle for debug only
                                    #print(
                                    #    "{head_sep:s}{body_msg:s}{foot_sep:s}".format(
                                    #        head_sep=f"{'=' * 80}\n",
                                    #        body_msg="[DEBUG]   UPDATE CHAT HISTORY DATA\n",
                                    #        foot_sep=f"{'=' * 80}\n"
                                    #    )
                                    #)
                                    #pp(
                                    #    object=new_chat_history,
                                    #    stream=stdout,
                                    #    indent=4 # Prefer tab over spaces indentation
                                    #)

                                    if len(new_chat_history) == 0: # pyright: ignore
                                        # Two scenarios can occured here:
                                        # 1. Incoming data completely matched stored data
                                        # => Do nothing. We don't want to waste disk
                                        #    I/O for update with zero changes.
                                        #
                                        # 2. Something's rising and it isn't the shield hero...
                                        # => Kindly ask user to submit a bug report
                                        #    to us so we can investigate this as I
                                        #    cannot think of one op top of my head.
                                        pass

                                    else:
                                        if isinstance(new_chat_history, list): # pyright: ignore
                                            for new_chat_convo in new_chat_history: # pyright: ignore
                                                # NOTE:
                                                # This might be hard to read because we're trying to be
                                                # dynamic by leverage the type check from ORM for running SQL
                                                # query. This code (in SQL syntax) is:
                                                #   UPDATE
                                                #       chatboxes
                                                #   SET
                                                #       details = details::JSONB || [new_chat_history]::JSONB
                                                #   WHERE
                                                #       chatboxes.id = config_id
                                                #   RETURNING
                                                #       chatboxes.name,
                                                #       chatboxes.details,
                                                #       chatboxes.id,
                                                #       chatboxes.create_on
                                                chatbox_stmt: Update = (
                                                    update(table=Chatboxes)
                                                    .where(Chatboxes.id == chatbox_session_id) # pyright: ignore
                                                    .values(new_chat_convo) # pyright: ignore
                                                    .returning(Chatboxes)
                                                )
                                                session.exec(statement=chatbox_stmt)
                                            session.commit()

                                        elif isinstance(new_chat_history, dict): # pyright: ignore
                                            # NOTE:
                                            # This might be hard to read because we're trying
                                            # to be dynamic by leverage the type check from
                                            # ORM for running SQL query. This code (in SQL
                                            # syntax) is:
                                            #   UPDATE
                                            #       chatboxes
                                            #   SET
                                            #       chatboxes['details'][chat_history_idx][current key] = <new value>
                                            #   WHERE
                                            #       chatboxes.id = chatbox_session_id
                                            #   RETURNING
                                            #       chatboxes.user_id,
                                            #       chatboxes.name,
                                            #       chatboxes.details
                                            chatbox_stmt: Update = (
                                                update(table=Chatboxes)
                                                .where(Chatboxes.id == chatbox_session_id) # pyright: ignore
                                                .values(new_chat_history)
                                                .returning(Chatboxes)
                                            )
                                            session.exec(statement=chatbox_stmt)
                                            session.commit()

                                except ConnectError as httpx_err:
                                    raise HTTPException(
                                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                        detail=f"{httpx_err}"
                                    )

                                except ConnectTimeout as httpx_err:
                                    raise HTTPException(
                                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                        detail=f"{httpx_err}"
                                    )

                        else:
                            # Update other data than chatbox details
                            pass

                else:
                    # We CANNOT update chatbox data without its ownership
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "status": "400 - Bad Request",
                            "message": "{trig:s}: {cond:s}".format(
                                trig="Chatbox update forbidden",
                                cond="Chatbox ownership (user ID) required for valid PATCH request!"
                            )
                        }
                    )

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
