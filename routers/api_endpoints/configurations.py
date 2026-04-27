### Core modules ###
from fastapi import (
    APIRouter,
    HTTPException,
    status
)
from sqlalchemy.sql.expression import BinaryExpression, update
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


### Internal modules ###
from ...apis.table_models.configurations import Configurations
from ...apis.data_models.configurations import (
    # For validation (Data Model)
    ConfigurationCreate,
    ConfigurationUpdate
)
from ...types.api_responses.configurations import (
    # For client responses (Responses Model)
    ConfigurationsPublicResponse,
    ConfigurationCreateResponse,
    ConfigurationPublicResponse,
    ConfigurationUpdateResponse
)


configs_v1_router: APIRouter = APIRouter(
    prefix="/api/v1/configs",
    tags=[APITag.config]
)


config_additional_responses: dict[int | str, dict[str, Any]] = {
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


@configs_v1_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=ConfigurationsPublicResponse
)
async def read_configs_v1(
    session: SessionDependency
) -> Any:
    configs_view: Sequence[Configurations] = session.exec(statement=select(Configurations)).all()
    total_configs: int = len(configs_view)

    if (total_configs == 0):
        return {
            "success": True,
            "count": total_configs, # 0
            "result": configs_view
        }
    else:
        return {
            "success": True,
            "count": total_configs, # all fetchable configs data
            "result": configs_view
        }


@configs_v1_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=ConfigurationCreateResponse,
    responses=config_additional_responses
)
async def create_config_v1(
    config: ConfigurationCreate,
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
        config_validate_data:   Configurations  = Configurations.model_validate(obj=config, strict=True)
        config_compatible_data: dict[str, Any]  = config_validate_data.model_dump(mode="json", exclude_unset=True)
        config_db:              Configurations  = Configurations(**config_compatible_data)

        session.add(instance=config_db)
        session.commit()
        session.refresh(instance=config_db)

        return {
            "success": True,
            "created": config_db
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


@configs_v1_router.get(
    path="/{config_id}",
    status_code=status.HTTP_200_OK,
    response_model=ConfigurationPublicResponse
)
async def read_config_v1(
    config_id: UUID7,
    session: SessionDependency
) -> Any:
    config_view: Configurations | None = session.get(entity=Configurations, ident=config_id)

    if config_view is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration Not Found!"
        )
    else:
        return {
            "success": True,
            "result": config_view
        }


@configs_v1_router.patch(
    path="/{config_id}",
    status_code=status.HTTP_200_OK,
    response_model=ConfigurationUpdateResponse
)
async def update_config_v1(
    config_id: UUID7,
    config: ConfigurationUpdate,
    session: SessionDependency
) -> Any:
    config_db: Configurations | None = session.get(entity=Configurations, ident=config_id)

    if config_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration Not Found!"
        )
    else:
        config_data: dict[str, Any] = config.model_dump(mode="json", exclude_unset=False)

        # Case 1: simple data updates
        if config_data["name"] is None:
            # Update other data than service name
            pass

        else:
            if config_data["name"] == config_db.name:
                # Matching config name in stored config data
                pass

            else:
                config_db.sqlmodel_update(obj=config_data)

                session.add(instance=config_db)
                session.commit()
                session.refresh(instance=config_db)

        # Case 2: complex data updates (JSONB data)
        if config_data["details"] is None:
            # Update other data than service option
            pass

        else:
            new_general_config:         dict[str, Any] = config_data["details"]["general"]
            new_query_analyser_config:  dict[str, Any] = config_data["details"]["query_analyser"]

            old_general_config:         dict[str, Any] = config_db.details["general"]           # pyright: ignore
            old_query_analyser_config:  dict[str, Any] = config_db.details["query_analyser"]    # pyright: ignore

            diff_config_data = {}

            # Case 2a: simple dict updates within complex data
            if new_general_config == old_general_config:
                print("Same general config data found...")

            else:
                diff_general_config: dict[str, Any] = {
                    key: value
                    for (key, value) in new_general_config.items()
                    if value != old_general_config[key]
                }

                if len(diff_general_config) == 0:
                    pass

                else:
                    print(f"General config differences: {diff_general_config}")
                    update_general_config: dict[BinaryExpression, Any] = {
                        Configurations.details["general"][key]: value # pyright: ignore
                        for key, value in diff_general_config.items()
                    }

                    config_stmt = (
                        update(table=Configurations)
                        .where(Configurations.id == config_id) # pyright: ignore
                        .values(update_general_config)
                        .returning(Configurations)
                    )
                    session.exec(statement=config_stmt)
                    session.commit()

                    diff_config_data.setdefault(
                        "details",
                        {}
                    )["general"] = diff_general_config

            if config_data["details"]["query_analyser"] == config_db.details["query_analyser"]:
                print("Same query analyser config data found...")

            else:
                diff_query_analyser_config: dict[str, Any] = {
                    key: value
                        for (key, value) in new_query_analyser_config.items()
                    if value != old_query_analyser_config[key]
                }

                if len(diff_query_analyser_config) == 0:
                    pass

                else:
                    print(f"Query Analyser config differences: {diff_query_analyser_config}")
                    update_query_analyser_config: dict[BinaryExpression, Any] = {
                        Configurations.details["query_analyser"][key]: value # pyright: ignore
                        for key, value in diff_query_analyser_config.items()
                    }

                    config_stmt = (
                        update(table=Configurations)
                        .where(Configurations.id == config_id) # pyright: ignore
                        .values(update_query_analyser_config)
                        .returning(Configurations)
                    )
                    session.exec(statement=config_stmt)
                    session.commit()

                    diff_config_data.setdefault(
                        "details",
                        {}
                    )["query_analyser"] = diff_query_analyser_config

            # Case 2b: complex list of dict updates within complex data
            if config_data["details"]["services"] == config_db.details["services"]:
                print("Same services config data found...")

            if diff_config_data is not None:
                print(f"New config for update: {diff_config_data}")

        return {
            "success": True,
            "updated": config_db
        }
