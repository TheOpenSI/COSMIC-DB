### Core modules ###


### Type hints ###
from typing import Any


### Internal modules ###



LLM_ROLE: str = 'assistant'


OPENAI_GET_EXTRA_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {
        "description": "Requested Data Not Found",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "status": "404 - Not Found",
                        "message": "string"
                    }
                }
            }
        }
    }
}

OPENAI_UPDATE_EXTRA_RESPONSES: dict[int | str, dict[str, Any]] = {
    **OPENAI_GET_EXTRA_RESPONSES,
    409: {
        "description": "Foreign Key Integrity Constraint Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "status": "409 - Conflict",
                        "message": "string"
                    }
                }
            }
        }
    }
}

OPENAI_DELETE_EXTRA_RESPONSES: dict[int | str, dict[str, Any]] = {
    **OPENAI_GET_EXTRA_RESPONSES
}
