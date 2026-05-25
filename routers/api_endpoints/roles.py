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
from ...apis.table_models.roles import Roles
from ...apis.data_models.roles import (
    # For validation (Data Model)
    RoleCreate,
    RoleUpdate
)
from ...types.api_responses.roles import (
    # For client responses (Responses Model)
    RolesPublicResponse,
    RoleCreateResponse,
    RolePublicResponse,
    RoleUpdateResponse,
    RoleDeleteResponse
)


roles_v1_router: APIRouter = APIRouter(
    prefix="/api/v1/roles",
    tags=[APITag.role]
)


@roles_v1_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=RolesPublicResponse
)
async def read_roles_v1(
    session: SessionDependency
) -> Any:
    roles_view: Sequence[Roles] = session.exec(statement=select(Roles)).all()
    total_roles: int = len(roles_view)

    if (total_roles == 0):
        return {
            "success": True,
            "count": total_roles, # 0
            "result": roles_view
        }
    else:
        return {
            "success": True,
            "count": total_roles, # all fetchable role data
            "result": roles_view
        }


@roles_v1_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=RoleCreateResponse
)
async def create_role_v1(
    role: RoleCreate,
    session: SessionDependency
) -> Any:
    try:
        role_db: Roles = Roles.model_validate(obj=role, strict=True)

        session.add(instance=role_db)
        session.commit()
        session.refresh(instance=role_db)

        return {
            "success": True,
            "created": role_db
        }

    except Exception as fastapi_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "Internal Server Error",
                "message": str(object=fastapi_err)
            }
        )


@roles_v1_router.get(
    path="/{role_id}",
    status_code=status.HTTP_200_OK,
    response_model=RolePublicResponse
)
async def read_role_v1(
    role_id: UUID,
    session: SessionDependency
) -> Any:
    role_view: Roles | None = session.get(entity=Roles, ident=role_id)

    if role_view is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role Not Found!"
        )
    else:
        return {
            "success": True,
            "result": role_view
        }


@roles_v1_router.patch(
    path="/{role_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoleUpdateResponse
)
async def update_role_v1(
    role_id: UUID,
    role: RoleUpdate,
    session: SessionDependency
) -> Any:
    role_db: Roles | None = session.get(entity=Roles, ident=role_id)

    if role_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role Not Found!"
        )
    else:
        role_data: dict[str, Any] = role.model_dump(exclude_unset=True)
        role_db.sqlmodel_update(obj=role_data)

        session.add(instance=role_db)
        session.commit()
        session.refresh(instance=role_db)

        return {
            "success": True,
            "updated": role_db
        }


@roles_v1_router.delete(
    path="/{role_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoleDeleteResponse
)
async def delete_role_v1(
    role_id: UUID,
    session: SessionDependency
) -> Any:
    role_gone: Roles | None = session.get(entity=Roles, ident=role_id)

    if role_gone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role Not Found!"
        )
    else:
        session.delete(instance=role_gone)
        session.commit()

        return {
            "success": True,
            "deleted": role_gone
        }
