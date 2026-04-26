### Core modules ###
from pydantic import BaseModel, ConfigDict


### Type hints ###


### Internal modules ###
from ..cores.db import cosmic_db_configs



#=============================================================================#
#   Pydantic validation for 'option' JSONB field in each selected services    #
#=============================================================================#
class ChessServiceOptions(BaseModel):
    """docstring for ChessServiceOptions."""
    model_config = ConfigDict(extra="forbid")

    # TODO:
    # This need to be defined and stored from an external mounted volume data
    # that's related to CoSMIC container. After a PR for this create and merged,
    # change this to `NOTE` and adjust the comment explanation.
    executable_path: str = "/app/bin/"


class MemoryServiceOptions(BaseModel):
    """docstring for MemoryServiceOptions."""
    model_config = ConfigDict(extra="forbid")

    # TODO:
    # This need to be defined and stored from an external mounted volume data
    # that's related to vector database container. After a PR for this create
    # and merged, change this to `NOTE` and adjust the comment explanation.
    vector_db_path: str = "/app/qdrant/"


class CodeGenerationServiceOptions(BaseModel):
    """docstring for CodeGenerationServiceOptions."""
    model_config = ConfigDict(extra="forbid")

    top_k:                      int     = 10
    retrieve_score_threshold:   float   = 0.7
    # TODO:
    # This need to be defined and stored from an external mounted volume data
    # that's related to vector database container. After a PR for this create
    # and merged, change this to `NOTE` and adjust the comment explanation.
    vector_db_path:             str     = "/app/qdrant/"


class GeneralQuestionAnsweringServiceOptions(BaseModel):
    """docstring for GeneralQuestionAnsweringServiceOptions."""
    model_config = ConfigDict(extra="forbid")

    # No extra options needed for this service.
    pass


class AcademicGovernanceServiceOptions(BaseModel):
    """docstring for AcademicGovernanceServiceOptions."""
    model_config = ConfigDict(extra="forbid")

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



#=============================================================================#
#   Pydantic validation for parent JSONB fields for default configurations    #
#=============================================================================#
class GeneralConfigs(BaseModel):
    """docstring for GeneralConfigs."""
    model_config = ConfigDict(extra="forbid")

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
    model_config = ConfigDict(extra="forbid")

    # NOTE:
    # On 'Configs' page, there'll be an option to apply similar configs as the
    # general unless wanting to customise manually by the admin user.
    model:          str     = "qwen3.6:35b"
    is_quantised:   bool    = True


class ServicesConfigs(BaseModel):
    """docstring for ServicesConfigs."""
    model_config = ConfigDict(extra="forbid")

    name:   str
    option: ServiceOptions | dict[None, None] = {}



#=============================================================================#
#       Pydantic validation for default configurations (JSONB type)           #
#=============================================================================#
class ConfigurationSchema(BaseModel):
    """docstring for ConfigurationSchema."""
    model_config = ConfigDict(extra="forbid")

    general:        GeneralConfigs | None
    query_analyser: QueryAnalyserConfigs | None
    services:       list[ServicesConfigs] | list[None] = []
