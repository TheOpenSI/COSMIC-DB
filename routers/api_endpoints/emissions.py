### Core modules ###
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status
)
from sqlmodel import select


### Type hints ###
from typing_extensions import (
    Annotated,
    Any,
    Sequence
)
from ...types.tags import APITag
from pydantic.types import UUID7
from sqlalchemy.exc import IntegrityError


### Internal modules ###
from ...cores.db import SessionDependency
from ...apis.table_models.emissions import Emissions
from ...apis.data_models.emissions import (
    # For validation (Data Model)
    EmissionCreate
)
from ...types.api_responses.emissions import (
    # For client responses (Responses Model)
    EmissionsPublicResponse,
    EmissionCreateResponse,
    EmissionDeleteResponse
)
from ...types.filter_params import (
    EmissionFilterParams
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
    session: SessionDependency,
    filter_query: Annotated[
        EmissionFilterParams,
        Query(
            title="Emissions Filter",
            description="Filter emissions data by `user_id` or `emission_id`.",
            strict=True
        )
    ]
) -> Any:
    statement = select(Emissions)

    if filter_query.emission_id is not None:
        statement = statement.where(Emissions.id == filter_query.emission_id)

    if filter_query.user_id is not None:
        statement = statement.where(Emissions.user_id == filter_query.user_id)

    emissions_view: Sequence[Emissions] = session.exec(statement=statement).all()

    return {
        "success": True,
        "count": len(emissions_view),
        "result": emissions_view
    }


@emissions_v1_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=EmissionCreateResponse
)
async def create_emission_v1(
    emission: EmissionCreate,
    session: SessionDependency
) -> Any:
    try:
        # NOTE:
        # Anyone might wonder why didn't we do any sort of creation validation
        # logic here? Since this particular endpoint here is being used to create
        # new Carbon emission data per user query, it's actually valid usecase to
        # have duplicate data in the db. Why would it be? Because, well, SLMs can
        # use the same amount of energy and effort to give users responses that
        # would sound reasonable to their queries (whether it's exactly the same
        # or not). Besides, users are **REDACTED** anyways :)
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


    except IntegrityError as sqlalchemy_exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": "409 - Conflict",
                "message": f"{sqlalchemy_exc}"
            }
        )


@emissions_v1_router.delete(
    path="/{emission_id}",
    status_code=status.HTTP_200_OK,
    response_model=EmissionDeleteResponse
)
async def delete_emission_v1(
    emission_id: UUID7,
    session: SessionDependency
) -> Any:
    emission_gone: Emissions | None = session.get(
        entity=Emissions,
        ident=emission_id
    )

    if emission_gone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emission Record Not Found!"
        )

    else:
        session.delete(instance=emission_gone)
        session.commit()

        return {
            "success": True,
            "deleted": emission_gone
        }
