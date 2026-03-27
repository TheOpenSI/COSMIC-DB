### Core modules ###
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, select


### Type hints ###
from sqlmodel.sql.expression import SelectOfScalar
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound
)


### Internal modules ###
from ..cores.db import cosmic_db_engine
from ..apis.models import (
    Roles,
    UserRoleLink,
    Users
)


def populate_default_role() -> None:
    default_roles: list[dict[str, str | None]] = [
        {
            "name": "Admin",
            "desc": None
        },
        {
            "name": "User",
            "desc": None
        }
    ]

    for default_role in default_roles:
        default_role_data: Roles = Roles(
            name=str(object=default_role["name"]),
            desc=default_role["desc"]
        )

        with Session(bind=cosmic_db_engine) as session:
            exist_role_stmt: SelectOfScalar[Roles] = select(Roles).where(Roles.name == str(object=default_role["name"]))
            exist_role_data: Roles | None = session.exec(statement=exist_role_stmt).first()

            if exist_role_data is None:
                # Add default role
                session.add(instance=default_role_data)
                session.commit()
                session.refresh(instance=default_role_data)
            else:
                # Simply skip it
                print("Role existed, skipping...")
                break

    return None


def populate_default_user() -> None:
    default_user_data: Users = Users(
        # TODO: implement hased password + these goes into '.env' file instead
        name="cosmic",
        email="opensi@canberra.edu.au",
        password="cosmic"
    )

    with Session(bind=cosmic_db_engine) as session:
        exist_user_stmt: SelectOfScalar[Users] = select(Users).where(
            Users.name == "cosmic",
            Users.email == "opensi@canberra.edu.au"
        )
        exist_user_data: Users | None = session.exec(statement=exist_user_stmt).first()

        if exist_user_data is None:
            # Add default user
            session.add(instance=default_user_data)
            session.commit()
            session.refresh(instance=default_user_data)
        else:
            # Simply skip it
            print("User existed, skipping...")
            pass

    return None


# NOTE: only run this after populate data for `Roles` & `Users` table
def populate_default_account() -> None:
    with Session(bind=cosmic_db_engine) as session:
        try:
            exist_user_data: UUID = session.exec(
                statement=select(
                    Users.id
                )
            ).one()
            exist_role_data: UUID = session.exec(
                statement=select(
                    Roles.id
                ).where(Roles.name == "Admin")
            ).one()

            default_account_data: UserRoleLink = UserRoleLink(
                user_id=exist_user_data,
                role_id=exist_role_data
            )

            exist_default_account_data: UserRoleLink | None = session.exec(
                statement=select(
                    UserRoleLink
                ).where(
                    UserRoleLink.user_id == exist_user_data,
                    UserRoleLink.role_id == exist_role_data
                )
            ).first()

            # TODO:
            # We should be reading from View table, not from join table
            # directly. However, SQLModel doesn't have a syntax to support SQL
            # View directly but it's wrapper (SQLAlchemy) does just recently.
            # It's a bit complex to set it up in OOP way to create SQL View
            # tables dynamcially so this'll be written in its own PR.
            if exist_default_account_data is None:
                # Add default account
                session.add(instance=default_account_data)
                session.commit()
                session.refresh(instance=default_account_data)
            else:
                # Simply skip it
                print("Initial account existed, skipping...")
                pass

        except MultipleResultsFound as sqlmodel_err:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "Serivce Unavailable",
                    "message": sqlmodel_err
                }
            )

        except NoResultFound as sqlmodel_err:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "Serivce Unavailable",
                    "message": sqlmodel_err
                }
            )

        except IntegrityError as sqlmodel_err:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "Serivce Unavailable",
                    "message": sqlmodel_err
                }
            )

        except Exception as fastapi_err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "status": "Internal Server Error",
                    "message": fastapi_err
                }
            )

        return None
