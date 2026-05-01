### Core modules ###
from typing import Annotated
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status
)
from sqlmodel import select


### Type hints ###
from typing_extensions import Any, Sequence
from ...types.tags import APITag
from pydantic.types import PositiveInt


### Internal modules ###
from ...cores.db import SessionDependency
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
            description="filter by active/deactive services.",
            strict=True
        )
    ]
) -> Any:
    if filter_query.active is None:
        services_view: Sequence[Services] = session.exec(statement=select(Services)).all()
        total_services: int = len(services_view)

        if (total_services == 0):
            return {
                "success": True,
                "count": total_services, # 0
                "result": services_view
            }
        else:
            return {
                "success": True,
                "count": total_services, # all fetchable service data
                "result": services_view
            }

    elif filter_query.active:
        active_services_view: Sequence[Services] = session.exec(statement=select(Services).where(Services.status == True)).all()
        total_services: int = len(active_services_view)

        if (total_services == 0):
            return {
                "success": True,
                "count": total_services, # 0
                "result": active_services_view
            }
        else:
            return {
                "success": True,
                "count": total_services, # all fetchable active service data
                "result": active_services_view
            }

    else:
        deactive_services_view: Sequence[Services] = session.exec(statement=select(Services).where(Services.status == False)).all()
        total_services: int = len(deactive_services_view)

        if (total_services == 0):
            return {
                "success": True,
                "count": total_services, # 0
                "result": deactive_services_view
            }
        else:
            return {
                "success": True,
                "count": total_services, # all fetchable deactive service data
                "result": deactive_services_view
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
        service_db: Services = Services.model_validate(obj=service, strict=True)

        session.add(instance=service_db)
        session.commit()
        session.refresh(instance=service_db)

        return {
            "success": True,
            "created": service_db
        }

    except Exception as fastapi_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "Internal Server Error",
                "message": str(object=fastapi_err)
            }
        )


@services_v1_router.get(
    path="/{service_id}",
    status_code=status.HTTP_200_OK,
    response_model=ServicePublicResponse
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
    response_model=ServiceUpdateResponse
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
        service_data: dict[str, Any] = service.model_dump(exclude_unset=True)
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
    response_model=ServiceDeleteResponse
)
async def delete_service_v1(
    service_id: PositiveInt,
    session: SessionDependency
) -> Any:
    service_gone: Services | None = session.get(entity=Services, ident=service_id)

    if service_gone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service Not Found!"
        )
    else:
        session.delete(instance=service_gone)
        session.commit()

        return {
            "success": True,
            "deleted": service_gone
        }
