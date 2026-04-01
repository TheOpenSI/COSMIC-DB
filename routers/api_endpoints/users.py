### Core modules ###
from fastapi import (
    APIRouter,
    HTTPException,
    status
)
from sqlmodel import select


### Type hints ###
from uuid import UUID
from typing_extensions import Any, Sequence
from ...types.tags import APITag


### Internal modules ###
from ...cores.db import SessionDependency
from ...apis.table_models.users import Users
from ...apis.data_models.users import (
    # For validation (Data Model)
    UserCreate,
    UserUpdate
)
from ...types.api_responses.users import (
    # For client responses (Responses Model)
    UsersPublicResponse,
    UserCreateResponse,
    UserPublicResponse,
    UserUpdateResponse,
    UserDeleteResponse
)


users_v1_router: APIRouter = APIRouter(
    prefix="/api/v1/users",
    tags=[APITag.user]
)


@users_v1_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=UsersPublicResponse
)
async def read_users_v1(
    session: SessionDependency
) -> Any:
    users_view: Sequence[Users] = session.exec(statement=select(Users)).all()
    total_users: int = len(users_view)

    if (total_users == 0):
        return {
            "success": True,
            "count": total_users, # 0
            "result": users_view
        }
    else:
        return {
            "success": True,
            "count": total_users, # all fetchable user data
            "result": users_view
        }


@users_v1_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserCreateResponse
)
async def create_user_v1(
    user: UserCreate,
    session: SessionDependency
) -> Any:
    try:
        user_db: Users = Users.model_validate(obj=user, strict=True)

        session.add(instance=user_db)
        session.commit()
        session.refresh(instance=user_db)

        return {
            "success": True,
            "created": user_db
        }

    except Exception as fastapi_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "Internal Server Error",
                "message": fastapi_err
            }
        )


@users_v1_router.get(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublicResponse
)
async def read_user_v1(
    user_id: UUID,
    session: SessionDependency
) -> Any:
    user_view: Users | None = session.get(entity=Users, ident=user_id)

    if user_view is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found!"
        )
    else:
        return {
            "success": True,
            "result": user_view
        }


@users_v1_router.patch(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserUpdateResponse
)
async def update_user_v1(
    user_id: UUID,
    user: UserUpdate,
    session: SessionDependency
) -> Any:
    user_db: Users | None = session.get(entity=Users, ident=user_id)

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found!"
        )
    else:
        user_data: dict[str, Any] = user.model_dump(exclude_unset=True)
        user_db.sqlmodel_update(obj=user_data)

        session.add(instance=user_db)
        session.commit()
        session.refresh(instance=user_db)

        return {
            "success": True,
            "updated": user_db
        }


@users_v1_router.delete(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserDeleteResponse
)
async def delete_user_v1(
    user_id: UUID,
    session: SessionDependency
) -> Any:
    user_gone: Users | None = session.get(entity=Users, ident=user_id)

    if user_gone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found!"
        )
    else:
        session.delete(instance=user_gone)
        session.commit()

        return {
            "success": True,
            "deleted": user_gone
        }
