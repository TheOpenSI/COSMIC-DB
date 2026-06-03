### Core modules ###
from sqlmodel import SQLModel


### Type hints ###


### Internal modules ###
from ...apis.data_models.users import (
    UserPublic,
    UserDelete
)



"""
Client responses format according to FE requirements.
"""
class UsersPublicResponse(SQLModel):
    success:    bool
    count:      int
    result:     list[UserPublic]


class UserCreateResponse(SQLModel):
    success:    bool
    created:    UserPublic


class UserPublicResponse(SQLModel):
    success:    bool
    result:     UserPublic


class UserUpdateResponse(SQLModel):
    success:    bool
    updated:    UserPublic


class UserDeleteResponse(SQLModel):
    success:    bool
    deleted:    UserDelete
