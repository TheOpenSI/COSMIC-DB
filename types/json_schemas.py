### Core modules ###
from pydantic import BaseModel, ConfigDict


### Type hints ###


### Internal modules ###
from ..cores.db import cosmic_db_configs



#=============================================================================#
#   Pydantic validation for parent JSONB fields for default configurations    #
#=============================================================================#
class GeneralConfigs(BaseModel):
    """docstring for GeneralConfigs."""
    model_config = ConfigDict(extra="forbid")

    provider:               str         = "ollama"
    model:                  str         = "qwen2.5:7b"
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
    model:          str     = "llama3.3:70b"
    is_quantised:   bool    = True



#=============================================================================#
#       Pydantic validation for default configurations (JSONB type)           #
#=============================================================================#
class ConfigurationSchema(BaseModel):
    """docstring for ConfigurationSchema."""
    model_config = ConfigDict(extra="forbid")

    general:        GeneralConfigs
    query_analyser: QueryAnalyserConfigs
