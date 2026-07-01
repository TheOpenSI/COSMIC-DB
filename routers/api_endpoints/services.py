### Core modules ###
from typing import Annotated
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status
)
from sqlmodel import (
    or_,
    select
)


### Type hints ###
from sqlmodel.sql.expression import SelectOfScalar
from typing_extensions import (
    Any,
    Sequence
)
from ...types.tags import APITag
from pydantic.types import PositiveInt
from fastapi.exceptions import ResponseValidationError


### Internal modules ###
from ...cores.db import SessionDependency
from ...cores.globals import (
    OPENAPI_GET_EXTRA_RESPONSES,
    OPENAPI_PATCH_EXTRA_RESPONSES,
    OPENAPI_DELETE_EXTRA_RESPONSES
)
from ...apis.table_models.services import Services
from ...apis.data_models.services import (
    # For validation (Data Model)
    ServiceCreate,
    ServiceUpdate
)
from ...types.api_responses.services import (
    # For client responses (Responses Model)
    ServicesPublicResponse,
    ServiceCreateResponse,
    ServicePublicResponse,
    ServiceUpdateResponse,
    ServiceDeleteResponse
)
from ...types.filter_params import (
    ServiceFilterParams
)


services_v1_router: APIRouter = APIRouter(
    prefix="/api/v1/services",
    tags=[APITag.service]
)


@services_v1_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=ServicesPublicResponse
)
async def read_services_v1(
    session: SessionDependency,
    filter_query: Annotated[
        ServiceFilterParams,
        Query(
            title="Services Filter",
            description="filter by active/deactive memory enabled/disabled services.",
            strict=True
        )
    ]
) -> Any:
    # Dynamic build SELECT queries with WHERE clause for filtering
    service_stmt: SelectOfScalar[Services] = select(Services)

    if filter_query.active is not None:
        service_stmt = service_stmt.where(Services.status == filter_query.active)

    if filter_query.memory_enable is not None:
        service_stmt = service_stmt.where(Services.memory_capability == filter_query.memory_enable)

    # Final result will differ depends on which SELECT query being executed if
    # filter applied or not
    services_view: Sequence[Services] = session.exec(statement=service_stmt).all()

    return {
        "success": True,
        "count": len(services_view),
        "result": services_view
    }


@services_v1_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=ServiceCreateResponse
)
async def create_service_v1(
    service: ServiceCreate,
    session: SessionDependency
) -> Any:
    try:
        # Only perform INSERT queries if incoming data not exist in the db
        service_stored_data: Services | None = session.exec(
            statement=select(Services).where(
                or_(
                    Services.name == service.name,
                    Services.desc == service.desc
                )
            )
        ).first()

        if service_stored_data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "status": "409 - Conflict",
                    "message": "A service with similar 'name' or 'desc' column data already exists"
                    }
                )

        else:
            service_db: Services = Services.model_validate(
                obj=service,
                strict=True
            )

            session.add(instance=service_db)
            session.commit()
            session.refresh(instance=service_db)

            return {
                "success": True,
                "created": service_db
            }


    except ResponseValidationError as fastapi_exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "status": "422 - Unprocessable Content",
                "message": f"{fastapi_exc}"
            }
        )


@services_v1_router.get(
    path="/{service_id}",
    status_code=status.HTTP_200_OK,
    response_model=ServicePublicResponse,
    responses={**OPENAPI_GET_EXTRA_RESPONSES}
)
async def read_service_v1(
    service_id: PositiveInt,
    session: SessionDependency
) -> Any:
    service_view: Services | None = session.get(entity=Services, ident=service_id)

    if service_view is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service Not Found!"
        )

    else:
        return {
            "success": True,
            "result": service_view
        }


@services_v1_router.patch(
    path="/{service_id}",
    status_code=status.HTTP_200_OK,
    response_model=ServiceUpdateResponse,
    responses={**OPENAPI_PATCH_EXTRA_RESPONSES}
)
async def update_service_v1(
    service_id: PositiveInt,
    service: ServiceUpdate,
    session: SessionDependency
) -> Any:
    service_db: Services | None = session.get(entity=Services, ident=service_id)

    if service_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service Not Found!"
        )

    else:
        service_data: dict[str, Any] = service.model_dump(
            mode="python",
            exclude_unset=True
        )

        # NOTE:
        # This's a wrapped method provided by SQLModel module so we can simply
        # "update" stored service data with new one without having to think of
        # the logic behind it. I couldn't find an actual reference to this
        # method from the module itself (not surprised much since its part of
        # FastAPI) so that I can understand the usecase of it better. However,
        # these 2 sources below are my best attempt to justify the usage here:
        # 1. https://sqlmodel.tiangolo.com/tutorial/fastapi/update/#update-the-hero-in-the-database
        # 2. https://deepwiki.com/fastapi/sqlmodel/3-database-operations#partial-updates-with-multiple-models

        # Only perform UPDATE queries if incoming data differ from stored data
        service_db.sqlmodel_update(obj=service_data)

        session.add(instance=service_db)
        session.commit()
        session.refresh(instance=service_db)

        return {
            "success": True,
            "updated": service_db
        }


@services_v1_router.delete(
    path="/{service_id}",
    status_code=status.HTTP_200_OK,
    response_model=ServiceDeleteResponse,
    responses={**OPENAPI_DELETE_EXTRA_RESPONSES}
)
async def delete_service_v1(
    service_id: PositiveInt,
    session: SessionDependency
) -> Any:
    service_gone: Services | None = session.get(
        entity=Services,
        ident=service_id
    )

    if service_gone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service Not Found!"
        )

    else:
        if service_gone.status != False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "status": "403 - Forbidden",
                    "message": "Please disable the service first before peforming this action!!"
                }
            )

        else:
            session.delete(instance=service_gone)
            session.commit()

            return {
                "success": True,
                "deleted": service_gone
            }
