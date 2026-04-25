"""pre_populate_configs_data

Revision ID: a3e40b0c0b7b
Revises: 8e266617f204
Create Date: 2026-04-20 19:37:59.722834

"""
from typing import (
    Any,
    Sequence,
    Union
)
from uuid import (
    UUID,
    uuid7
)
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from datetime import (
    datetime,
    timezone
)
from sqlalchemy.orm.session import Session
from pydantic import BaseModel
from cores.db import cosmic_db_configs



# revision identifiers, used by Alembic.
revision: str = 'a3e40b0c0b7b'
down_revision: Union[str, Sequence[str], None] = '8e266617f204'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



#=============================================================================#
# Validate JSON column with Pydantic, copied from the `types/api_responses`   #
# directory due to how Alembic works                                          #
#=============================================================================#
class ChessServiceOptions(BaseModel):
    """docstring for ChessServiceOptions."""
    # TODO:
    # This need to be defined and stored from an external mounted volume data
    # that's related to CoSMIC container. After a PR for this create and merged,
    # change this to `NOTE` and adjust the comment explanation.
    executable_path: str = "/app/bin/"


class MemoryServiceOptions(BaseModel):
    """docstring for MemoryServiceOptions."""
    # TODO:
    # This need to be defined and stored from an external mounted volume data
    # that's related to vector database container. After a PR for this create
    # and merged, change this to `NOTE` and adjust the comment explanation.
    vector_db_path: str = "/app/qdrant/"


class CodeGenerationServiceOptions(BaseModel):
    """docstring for CodeGenerationServiceOptions."""
    top_k:                      int     = 10
    retrieve_score_threshold:   float   = 0.7
    # TODO:
    # This need to be defined and stored from an external mounted volume data
    # that's related to vector database container. After a PR for this create
    # and merged, change this to `NOTE` and adjust the comment explanation.
    vector_db_path:             str     = "/app/qdrant/"


class GeneralQuestionAnsweringServiceOptions(BaseModel):
    """docstring for GeneralQuestionAnsweringServiceOptions."""
    # No extra options needed for this service.
    pass


class AcademicGovernanceServiceOptions(BaseModel):
    """docstring for AcademicGovernanceServiceOptions."""
    # No extra options needed for this service.
    pass


# Custom type declaration needed for able to use it as type-hint at compile
# time. For reference:
# https://docs.python.org/3/reference/simple_stmts.html#type
type ServiceOptions = (
    ChessServiceOptions                     |
    MemoryServiceOptions                    |
    CodeGenerationServiceOptions            |
    GeneralQuestionAnsweringServiceOptions  |
    AcademicGovernanceServiceOptions        |
    dict[None, None]
)


class GeneralConfigs(BaseModel):
    """docstring for GeneralConfigs."""
    provider:               str         = "ollama"
    model:                  str         = "qwen3.5:9b"
    is_quantised:           bool        = False
    seed:                   int         = 0
    # TODO:
    # These 2 need to be defined and stored from an external mounted volume data
    # That's related to CoSMIC container. After a PR for this create and merged,
    # change this to `NOTE` and adjust the comment explanation.
    default_knowledge_path: str         = "/app/data/default/"
    temp_knowledge_path:    str         = "/app/data/temp/"
    # NOTE:
    # Read specified key's value from `cosmic_config.env` file (for now until I
    # think of a better, more secure solution).
    api_key:                str | None  = cosmic_db_configs["OPENAI_API_KEY"]


class QueryAnalyserConfigs(GeneralConfigs):
    """docstring for QueryAnalyserConfigs."""
    # NOTE:
    # On 'Configs' page, there'll be an option to apply similar configs as the
    # general unless wanting to customise manually by the admin user.
    model:          str     = "qwen3.6:35b"
    is_quantised:   bool    = True



class ServicesConfigs(BaseModel):
    """docstring for ServicesConfigs."""
    name:   str
    option: ServiceOptions | dict[None, None] = {}


class ConfigurationSchema(BaseModel):
    """docstring for ConfigurationSchema."""
    general:        GeneralConfigs
    query_analyser: QueryAnalyserConfigs
    services:       list[ServicesConfigs] | list[None] = []



#=============================================================================#
#                   Actual migration script starts from here                  #
#=============================================================================#
def upgrade() -> None:
    """Upgrade schema."""
    # Define pre-population tables
    configs_table: sa.Table = op.create_table(
        'configurations',
        sa.Column('id', sa.UUID(as_uuid=True), autoincrement=False, nullable=False),
        sa.Column('name', sa.TEXT(length=None, collation=None), autoincrement=False, nullable=True),
        sa.Column('details', JSONB(none_as_null=True,astext_type=None), autoincrement=False, nullable=False),
        sa.Column('create_on', sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f(name='PK_CONFIGURATION_ID')),
        if_not_exists=True
    )

    # Temporary create a connection to database to get populated data from
    # `Services` table
    configs_bind: sa.Connection = op.get_bind()

    with Session(bind=configs_bind) as session:
        # Temporary define a minimal version of `Services` db table for querying.
        # This ensures the called column remains immutable even if the models
        # change later on
        services_minimal_table: sa.Table = sa.Table(
            'services',
            sa.MetaData(),
            sa.Column(
                'name',
                sa.VARCHAR(
                    length=100,
                    collation=None
                ),
                autoincrement=False,
                nullable=False
            ),
            autoload_with=configs_bind
        )
        services_stmt: sa.Select[tuple[Any]] = sa.select(services_minimal_table.c.name)
        services_name: Sequence[Any] = session.scalars(statement=services_stmt).all()

    # Dynamically build the needed value for `option` object in
    # `ServicesConfigs()` class
    services_configs: list[ServicesConfigs] | list[None] = []

    for name in services_name:
        # This might looks a bit confusing but essentially, it does this:
        # 'code_generation' ==> 'Code_Generation' ==> 'CodeGenerationServiceOptions'
        options_class_name: str = f"{name.title().replace("_", "")}ServiceOptions"
        options_class: str | None = globals().get(options_class_name)

        option: ServiceOptions | dict[None, None] = options_class()  \
            if options_class                                         \
            else {}

        services_configs.append(
            ServicesConfigs(
                name=name,
                option=option
            )
        )

    # Define data to pre-populate to 'Configurations' table
    configs_data: list[dict[str, UUID | str | dict[str, Any] | datetime]] = [
        {
            'id': uuid7(),
            'name': 'Default Configuration',
            # Need to use `model_dump()` method so Python can see the JSON data
            # as built-in dict type
            'details': ConfigurationSchema(
                general=GeneralConfigs(),
                query_analyser=QueryAnalyserConfigs(),
                services=services_configs
            ).model_dump(mode="json", exclude_unset=False),
            'create_on': datetime.now(tz=timezone.utc)
        }
    ]

    # Pre-populating in bulk (insertion order matters)
    op.bulk_insert(
        table=configs_table,
        rows=configs_data,
        multiinsert=True # Set to 'False' if pass in pre-populate data literally
    )

    return None


def downgrade() -> None:
    """Downgrade schema."""
    # Wipes table, any FK relationship, and its data automatically since this's
    # just a fresh run
    op.drop_table(
        table_name='configurations',
        schema='public',
        if_exists=True
    )

    return None
