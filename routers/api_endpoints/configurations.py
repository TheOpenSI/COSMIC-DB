### Core modules ###
from fastapi import (
    APIRouter,
    HTTPException,
    status
)
from sqlmodel import select
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.expression import (
    func,
    update
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
from sqlalchemy.sql.elements import (
    BinaryExpression,
    ColumnElement
)
from sqlalchemy.dialects.postgresql import JSONB


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
    ConfigurationUpdateResponse,
    ConfigurationDeleteResponse
)


configs_v1_router: APIRouter = APIRouter(
    prefix="/api/v1/configs",
    tags=[APITag.config]
)


config_additional_responses: dict[int | str, dict[str, Any]] = {
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
    response_model=ConfigurationUpdateResponse,
    responses=config_additional_responses
)
async def update_config_v1(
    config_id: UUID7,
    config: ConfigurationUpdate,
    session: SessionDependency
) -> Any:
    try:
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
                new_general_config:         dict[str, Any]              = config_data["details"]["general"]
                new_query_analyser_config:  dict[str, Any]              = config_data["details"]["query_analyser"]
                new_services_config:        list[dict[str, Any] | None] = config_data["details"]["services"]

                old_general_config:         dict[str, Any]              = config_db.details["general"]          # pyright: ignore
                old_query_analyser_config:  dict[str, Any]              = config_db.details["query_analyser"]   # pyright: ignore
                old_services_config:        list[dict[str, Any] | None] = config_db.details["services"]         # pyright: ignore


                # Case 2a: simple dict updates within complex data (general config data)
                if new_general_config == old_general_config:
                    # Incoming data matched stored data so no need to waste disk I/O
                    # for running update on nothing
                    pass

                else:
                    diff_general_config: dict[str, Any] = {
                        key: value
                        for (key, value) in new_general_config.items()
                        if value != old_general_config[key]
                    }

                    update_general_config: dict[ColumnElement, Any] = {
                        Configurations.details["general"][key]: value # pyright: ignore
                        for key, value in diff_general_config.items()
                    }

                    config_stmt: Update = (
                        update(table=Configurations)
                        .where(Configurations.id == config_id) # pyright: ignore
                        .values(update_general_config)
                        .returning(Configurations)
                    )
                    session.exec(statement=config_stmt)
                    session.commit()


                # Case 2a: simple dict updates within complex data (query analyser config data)
                if new_query_analyser_config == old_query_analyser_config:
                    # Incoming data matched stored data so no need to waste disk I/O
                    # for running update on nothing
                    pass

                else:
                    diff_query_analyser_config: dict[str, Any] = {
                        key: value
                        for (key, value) in new_query_analyser_config.items()
                        if value != old_query_analyser_config[key]
                    }

                    update_query_analyser_config: dict[ColumnElement, Any] = {
                        Configurations.details["query_analyser"][key]: value # pyright: ignore
                        for key, value in diff_query_analyser_config.items()
                    }

                    config_stmt: Update = (
                        update(table=Configurations)
                        .where(Configurations.id == config_id) # pyright: ignore
                        .values(update_query_analyser_config)
                        .returning(Configurations)
                    )
                    session.exec(statement=config_stmt)
                    session.commit()


                # Case 2b: complex list of dict updates within complex data
                if new_services_config == old_services_config:
                    # Incoming data matched stored data so no need to waste disk I/O
                    # for running update on nothing
                    pass

                else:
                    diff_services_config: BinaryExpression = Configurations.details["services"] # pyright: ignore


                    # Sub-case 2b: add services
                    if len(new_services_config) > len(old_services_config):
                        # NOTE:
                        # This might be hard to read because we're trying to be
                        # dynamic by leverage the type check from ORM for running SQL
                        # query. This code (in SQL syntax) is:
                        #   UPDATE
                        #       configurations
                        #   SET
                        #       details['services'] = details['services']::JSONB || [new_services_config]::JSONB
                        #   WHERE
                        #       configurations.id = config_id
                        #   RETURNING
                        #       configurations.name,
                        #       configurations.details,
                        #       configurations.id,
                        #       configurations.create_on
                        config_stmt: Update = (
                            update(table=Configurations)
                            .where(Configurations.id == config_id) # pyright: ignore
                            .values({
                                diff_services_config: (func.cast(diff_services_config, JSONB)).op("||")(func.cast(new_services_config, JSONB)) # pyright: ignore
                            })
                            .returning(Configurations)
                        )
                        session.exec(statement=config_stmt)
                        session.commit()


                    # Sub-case 2b: remove services
                    elif len(new_services_config) < len(old_services_config):
                        # NOTE:
                        # This might be hard to read because we're trying to be
                        # dynamic by leverage the type check from ORM for running SQL
                        # query. This code (in SQL syntax) is:
                        #   UPDATE
                        #       configurations
                        #   SET
                        #       details['services'] = [new_services_config]::JSONB
                        #   WHERE
                        #       configurations.id = config_id
                        #   RETURNING
                        #       configurations.name,
                        #       configurations.details,
                        #       configurations.id,
                        #       configurations.create_on
                        config_stmt: Update = (
                            update(table=Configurations)
                            .where(Configurations.id == config_id) # pyright: ignore
                            .values({
                                diff_services_config: func.cast(new_services_config, JSONB) # pyright: ignore
                            })
                        )
                        session.exec(statement=config_stmt)
                        session.commit()


                    # Sub-case 2b: modify services (only trigger if there is/are
                    # services enabled)
                    else:
                        # Service name CANNOT be modifed
                        forbid_services_config: list[str] = [
                            f"{old_service_config["name"]} --> {new_service_config["name"]}" # pyright: ignore
                            for (old_service_config, new_service_config) in zip(old_services_config, new_services_config)
                            if old_service_config["name"] != new_service_config["name"] # pyright: ignore
                        ]

                        if len(forbid_services_config) > 0:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail={
                                    "status": "400 - Bad Request",
                                    "message": "Service name update forbidden: {forbid:s}".format(
                                        forbid=f"{', '.join(forbid_services_config)}"
                                    )
                                }
                            )
                        else:
                            permit_services_config: dict[ColumnElement, dict[str, Any]] = {}

                            for (
                                idx_service_config,
                                (old_service_config, new_service_config)
                            ) in enumerate(
                                iterable=zip(
                                    old_services_config,
                                    new_services_config
                                ),
                                start=0
                            ):
                                # Service option CAN be modifed
                                if new_service_config["option"] != old_service_config["option"]: # pyright: ignore
                                    surgical_services_update: ColumnElement = diff_services_config[idx_service_config]["option"]
                                    permit_services_config[surgical_services_update] = new_service_config["option"] # pyright: ignore

                            # NOTE:
                            # This might be hard to read because we're trying to be
                            # dynamic by leverage the type check from ORM for running SQL
                            # query. This code (in SQL syntax) is:
                            #   UPDATE
                            #       configurations
                            #   SET
                            #       details['services'][index][option][<specific key>] = <new value>
                            #   WHERE
                            #       configurations.id = config_id
                            #   RETURNING
                            #       configurations.name,
                            #       configurations.details,
                            #       configurations.id,
                            #       configurations.create_on
                            config_stmt: Update = (
                                update(table=Configurations)
                                .where(Configurations.id == config_id) # pyright: ignore
                                .values(permit_services_config)
                            )
                            session.exec(statement=config_stmt)
                            session.commit()

            return {
                "success": True,
                "updated": config_db
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


@configs_v1_router.delete(
    path="/{config_id}",
    status_code=status.HTTP_200_OK,
    response_model=ConfigurationDeleteResponse
)
async def delete_config_v1(
    config_id: UUID7,
    session: SessionDependency
) -> Any:
    config_gone: Configurations | None = session.get(entity=Configurations, ident=config_id)

    if config_gone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration Not Found!"
        )
    else:
        session.delete(instance=config_gone)
        session.commit()

        return {
            "success": True,
            "deleted": config_gone
        }
