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
from sqlalchemy import extract, func
from fastapi.exceptions import ResponseValidationError


### Internal modules ###
from ...cores.db import SessionDependency
from ...apis.table_models.users import Users
from ...apis.table_models.emissions import Emissions
from ...apis.data_models.emissions import (
    # For validation (Data Model)
    EmissionsCreate
)
from ...types.api_responses.emissions import (
    # For client responses (Responses Model)
    EmissionsPublicResponse,
    EmissionsCreateResponse,
    EmissionsDeleteResponse,
    EmissionsMonthlyStatsResponse
)
from datetime import datetime, timezone
from ...types.filter_params_emissions import EmissionsFilterParams


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
        EmissionsFilterParams,
        Query(
            title="Emissions Filter",
            description="Filter emissions by user_id or emission_id.",
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

        # to validate if the provided user_id exists in the db
        user = session.get(entity=Users, ident=emission_db.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id: User does not exist!"
            )

        session.add(instance=emission_db)
        session.commit()
        session.refresh(instance=emission_db)

        return {
            "success": True,
            "created": emission_db
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

@emissions_v1_router.get(
    path="/stats/monthly",
    status_code=status.HTTP_200_OK,
    response_model=EmissionsMonthlyStatsResponse,
)
async def read_emissions_monthly_stats_v1(
    session: SessionDependency,
) -> Any:
    target_year = datetime.now(tz=timezone.utc).year

    statement = (
        select(
            extract("month", Emissions.timestamp).label("month"),
            func.sum(Emissions.emissions).label("total"),
        )
        .where(extract("year", Emissions.timestamp) == target_year)
        .group_by(extract("month", Emissions.timestamp))
    )

    rows = session.exec(statement).all()

    # Build 12-slot array: index 0 = Jan, null if no rows for that month
    monthly_totals: list[float | None] = [None] * 12
    for row in rows:
        month_index = int(row.month) - 1  # SQL month is 1–12
        monthly_totals[month_index] = float(row.total)

    return {
        "success": True,
        "year": target_year,
        "monthly_totals": monthly_totals,
    }


@emissions_v1_router.delete(
    path="/{emission_id}",
    status_code=status.HTTP_200_OK,
    response_model=EmissionsDeleteResponse
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


