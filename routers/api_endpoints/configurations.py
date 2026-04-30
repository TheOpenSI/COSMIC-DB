### Core modules ###
from fastapi import (
    APIRouter,
    HTTPException,
    status
)
from sqlmodel import select
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.expression import update


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
from sqlalchemy.sql.elements import ColumnElement


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
            config_data: dict[str, Any] = config.model_dump(mode="json", exclude_unset=True)

            # Case 1: full data updates
            if all(key in config_data for key in ("name", "details")):
                config_name:    str                         = config_data["name"]
                config_details: dict[str, dict[str, Any]]   = config_data["details"]

                config_db.name      = config_name
                config_db.details   = config_details # pyright: ignore

                session.add(instance=config_db)
                session.commit()
                session.refresh(instance=config_db)


            # Case 2: partial data updates
            else:
                # Case 2a: partial data updates (config name)
                if "name" in config_data:
                    config_name: str = config_data["name"]

                    if config_name == config_db.name:
                        # Incoming data matched stored data so no need to
                        # waste disk I/O for running update on nothing
                        pass

                    else:
                        config_db.sqlmodel_update(obj=config_data)

                        session.add(instance=config_db)
                        session.commit()
                        session.refresh(instance=config_db)

                else:
                    # Update other data than config name
                    pass


                # Case 2b: partial data updates (config details)
                if "details" in config_data:
                    config_details:         dict[str, dict[str, Any]]   = config_data["details"]

                    general_config:         dict[str, Any]              = config_details["general"]
                    query_analyser_config:  dict[str, Any]              = config_details["query_analyser"]

                    new_config:             dict[ColumnElement, Any]    = {}


                    # Sub-case 2b - Scenario 1:
                    # General configs surgical updates
                    if general_config == config_db.details["general"]: # pyright: ignore
                        # Incoming data matched stored data so no need to
                        # waste disk I/O for running update on nothing
                        pass

                    else:
                        for (key, value) in general_config.items():
                            if value != config_db.details["general"][key]: # pyright: ignore
                                new_config[Configurations.details["general"][key]] = value # pyright: ignore


                    # Sub-case 2b - Scenario 2:
                    # Query Analyser configs surgical updates
                    if query_analyser_config == config_db.details["query_analyser"]: # pyright: ignore
                        # Incoming data matched stored data so no need to
                        # waste disk I/O for running update on nothing
                        pass

                    else:
                        for (key, value) in query_analyser_config.items():
                            if value != config_db.details["query_analyser"][key]: # pyright: ignore
                                new_config[Configurations.details["query_analyser"][key]] = value # pyright: ignore


                    #TODO: some sort of `verbose` argument toggle for debug only
                    #print(
                    #    "{head_sep:s}{body_msg:s}{foot_sep:s}".format(
                    #        head_sep=f"{'=' * 80}\n",
                    #        body_msg="[DEBUG]   UPDATE DEFAULT CONFIG DATA\n",
                    #        foot_sep=f"{'=' * 80}\n"
                    #    )
                    #)
                    #pp(
                    #    object=new_config,
                    #    stream=stdout,
                    #    indent=4 # Prefer tab over spaces indentation
                    #)

                    if len(new_config) == 0:
                        # Two scenarios can occured here:
                        # 1. Incoming data completely matched stored data
                        # => Do nothing. We don't want to waste disk
                        #    I/O for update with zero changes.
                        #
                        # 2. Something's rising and it isn't the shield hero...
                        # => Kindly ask user to submit a bug report
                        #    to us so we can investigate this as I
                        #    cannot think of one op top of my head.
                        pass

                    else:
                        # NOTE:
                        # This might be hard to read because we're trying
                        # to be dynamic by leverage the type check from
                        # ORM for running SQL query. This code (in SQL
                        # syntax) is:
                        #   UPDATE
                        #       configurations
                        #   SET
                        #       configurations['details'][config_type][current key] = <new value>
                        #   WHERE
                        #       configurations.id = config_id
                        #   RETURNING
                        #       configurations.user_id,
                        #       configurations.name,
                        #       configurations.details
                        config_stmt: Update = (
                            update(table=Configurations)
                            .where(Configurations.id == config_id) # pyright: ignore
                            .values(new_config)
                            .returning(Configurations)
                        )
                        session.exec(statement=config_stmt)
                        session.commit()

                else:
                    # Update other data than config details
                    pass

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
