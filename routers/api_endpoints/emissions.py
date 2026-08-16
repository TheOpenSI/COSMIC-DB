### Core modules ###
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status
)
from sqlalchemy.sql import (
    select,
    extract,
    func
)
from datetime import (
    datetime,
    timezone
)


### Type hints ###
from typing_extensions import (
    Annotated,
    Any
)
from ...types.tags import APITag
from pydantic.types import UUID7
from sqlalchemy.exc import IntegrityError
from ...types.filter_params import EmissionFilterParams


### Internal modules ###
from ...cores.db import SessionDependency
from ...cores.globals import (
    OPENAPI_POST_EXTRA_RESPONSES,
    OPENAPI_DELETE_EXTRA_RESPONSES,
    MONTH_LABELS,
    get_rolling_year_months,
)
from ...apis.table_models.emissions import Emissions
from ...apis.data_models.emissions import (
    # For validation (Data Model)
    EmissionCreate
)
from ...types.api_responses.emissions import (
    # For client responses (Responses Model)
    EmissionsPublicResponse,
    EmissionCreateResponse,
    EmissionDeleteResponse,
    EmissionsMonthlyStatsResponse,
    EmissionsUserSummaryResponse,
    EmissionsUserRollingResponse,
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
    response_model=EmissionCreateResponse,
    responses={**OPENAPI_POST_EXTRA_RESPONSES}
)
async def create_emission_v1(
    emission: EmissionCreate,
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


@emissions_v1_router.get(
    path="/stats",
    status_code=status.HTTP_200_OK,
    response_model=EmissionsMonthlyStatsResponse,
)
async def read_emissions_system_stats_v1(
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


@emissions_v1_router.get(
    path="/stats/{user_id}/summary",
    status_code=status.HTTP_200_OK,
    response_model=EmissionsUserSummaryResponse,
)
async def read_emissions_user_summary_v1(
    user_id: UUID7,
    session: SessionDependency,
) -> Any:
    statement = (
        select(
            func.coalesce(func.sum(Emissions.emissions), 0).label("total_emissions"),
            func.coalesce(func.sum(Emissions.cpu_power), 0).label("total_cpu_power"),
            func.coalesce(func.sum(Emissions.gpu_power), 0).label("total_gpu_power"),
        )
        .where(Emissions.user_id == user_id)
    )

    row = session.exec(statement).one()

    return {
        "success": True,
        "user_id": user_id,
        "total_emissions": float(row.total_emissions),
        "total_cpu_power": float(row.total_cpu_power),
        "total_gpu_power": float(row.total_gpu_power),
    }


@emissions_v1_router.get(
    path="/stats/{user_id}/rolling",
    status_code=status.HTTP_200_OK,
    response_model=EmissionsUserRollingResponse,
)
async def read_emissions_user_rolling_v1(
    user_id: UUID7,
    session: SessionDependency,
    months: int = Query(default=3, ge=3, le=12),
) -> Any:
    if months not in (3, 6, 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="months must be 3, 6, or 12",
        )

    year_months = get_rolling_year_months(months)
    window_start = datetime(
        year_months[0][0],
        year_months[0][1],
        1,
        tzinfo=timezone.utc,
    )

    statement = (
        select(
            extract("year", Emissions.timestamp).label("year"),
            extract("month", Emissions.timestamp).label("month"),
            func.sum(Emissions.emissions).label("total"),
        )
        .where(Emissions.user_id == user_id)
        .where(Emissions.timestamp >= window_start)
        .group_by(
            extract("year", Emissions.timestamp),
            extract("month", Emissions.timestamp),
        )
    )

    rows = session.exec(statement).all()
    totals_by_year_month = {
        (int(row.year), int(row.month)): float(row.total)
        for row in rows
    }

    spans_multiple_years = len({year for year, _ in year_months}) > 1
    labels: list[str] = []
    totals: list[float | None] = []

    for year, month in year_months:
        if spans_multiple_years:
            labels.append(f"{MONTH_LABELS[month - 1]} '{str(year)[2:]}'")
        else:
            labels.append(MONTH_LABELS[month - 1])

        totals.append(totals_by_year_month.get((year, month)))

    return {
        "success": True,
        "user_id": user_id,
        "months": months,
        "labels": labels,
        "totals": totals,
    }


@emissions_v1_router.delete(
    path="/{emission_id}",
    status_code=status.HTTP_200_OK,
    response_model=EmissionDeleteResponse,
    responses={**OPENAPI_DELETE_EXTRA_RESPONSES}
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
