### Core modules ###
from fastapi import (
    APIRouter,
    HTTPException,
    status
)
from sqlmodel import select


### Type hints ###
from uuid import UUID
from typing_extensions import Annotated, Any, Sequence
from ...types.tags import APITag
from fastapi import Query


### Internal modules ###
from ...cores.db import SessionDependency
from ...apis.table_models.users import Users
from ...apis.table_models.chatboxes import Chatboxes
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
from ...types.filter_params_emissions import EmissionsFilterParams


emissions_v1_router: APIRouter = APIRouter(
    prefix="/api/v1/emissions",
    tags=[APITag.emission]
)





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
        user = session.get(entity=Users, ident=emission_db.user_id) # to validate if the provided user_id exists in the db
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
    
    except HTTPException as http_exc:
            raise http_exc    # to raise the 400 error for invalid user_id or chat_id without being caught by the generic exception handler below
        

    except Exception as fastapi_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "Internal Server Error",
                "message": str(object=fastapi_err)
            }
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
            description="Filter emissions by user_id, chat_id or emission_id.",
            strict=True
        )
    ]
) -> Any:
    try:
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

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "Internal Server Error",
                "message": str(e)   
            }
        )

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