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
from ...apis.table_models.emissions import Emissions
from ...apis.data_models.emissions import (
    EmissionsCreate,
)
from ...types.api_responses.emissions import (
    EmissionsPublicResponse,
    EmissionsCreateResponse,
    EmissionsPublicSingleResponse,
    EmissionsDeleteResponse,
)


emissions_v1_router: APIRouter = APIRouter(
    prefix="/api/v1/emissions",
    tags=[APITag.emission]
)


@emissions_v1_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=EmissionsPublicResponse
)
async def read_emissions_v1(
    session: SessionDependency
) -> Any:
    emissions_view: Sequence[Emissions] = session.exec(
        statement=select(Emissions)
    ).all()
    total: int = len(emissions_view)

    return {
        "success": True,
        "count": total,
        "result": emissions_view
    }


@emissions_v1_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=EmissionsCreateResponse
)
async def create_emission_v1(
    emission: EmissionsCreate,
    session: SessionDependency
) -> Any:
    try:
        emission_db: Emissions = Emissions.model_validate(
            obj=emission,
            strict=True
        )

        session.add(instance=emission_db)
        session.commit()
        session.refresh(instance=emission_db)

        return {
            "success": True,
            "created": emission_db
        }

    except Exception as fastapi_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "Internal Server Error",
                "message": str(object=fastapi_err)
            }
        )


@emissions_v1_router.get(
    path="/{emission_id}",
    status_code=status.HTTP_200_OK,
    response_model=EmissionsPublicSingleResponse
)
async def read_emission_v1(
    emission_id: UUID,
    session: SessionDependency
) -> Any:
    emission_view: Emissions | None = session.get(
        entity=Emissions,
        ident=emission_id
    )

    if emission_view is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emission record not found!"
        )

    return {
        "success": True,
        "result": emission_view
    }


@emissions_v1_router.get(
    path="/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=EmissionsPublicResponse
)
async def read_emissions_by_user_v1(
    user_id: str,
    session: SessionDependency
) -> Any:
    emissions_view: Sequence[Emissions] = session.exec(
        statement=select(Emissions).where(Emissions.user_id == user_id)
    ).all()
    total: int = len(emissions_view)

    return {
        "success": True,
        "count": total,
        "result": emissions_view
    }


@emissions_v1_router.get(
    path="/chat/{chat_id}",
    status_code=status.HTTP_200_OK,
    response_model=EmissionsPublicResponse
)
async def read_emissions_by_chat_v1(
    chat_id: str,
    session: SessionDependency
) -> Any:
    emissions_view: Sequence[Emissions] = session.exec(
        statement=select(Emissions).where(Emissions.chat_id == chat_id)
    ).all()
    total: int = len(emissions_view)

    return {
        "success": True,
        "count": total,
        "result": emissions_view
    }


@emissions_v1_router.delete(
    path="/{emission_id}",
    status_code=status.HTTP_200_OK,
    response_model=EmissionsDeleteResponse
)
async def delete_emission_v1(
    emission_id: UUID,
    session: SessionDependency
) -> Any:
    emission_gone: Emissions | None = session.get(
        entity=Emissions,
        ident=emission_id
    )

    if emission_gone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emission record not found!"
        )

    session.delete(instance=emission_gone)
    session.commit()

    return {
        "success": True,
        "deleted": emission_gone
    }