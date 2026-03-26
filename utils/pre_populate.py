### Core modules ###
from sqlmodel import Session, select


### Type hints ###
from sqlmodel.sql.expression import SelectOfScalar


### Internal modules ###
from ..cores.db import cosmic_db_engine
from ..apis.models import Roles


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
