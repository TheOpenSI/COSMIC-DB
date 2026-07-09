### Core modules ###


### Type hints ###
from typing import Any


### Internal modules ###



LLM_ROLE: str = 'assistant'


OPENAPI_GET_EXTRA_RESPONSES: dict[int | str, dict[str, Any]] = {
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

OPENAPI_POST_EXTRA_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {
        "description": "Invalid Payload Received",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "status": "400 - Bad Request",
                        "message": "string"
                    }
                }
            }
        }
    },
    409: {
        "description": "Foreign Key Integrity Constraint Error / Matching Data Found",
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

OPENAPI_PATCH_EXTRA_RESPONSES: dict[int | str, dict[str, Any]] = {
    **OPENAPI_GET_EXTRA_RESPONSES,
    **OPENAPI_POST_EXTRA_RESPONSES
}

OPENAPI_DELETE_EXTRA_RESPONSES: dict[int | str, dict[str, Any]] = {
    **OPENAPI_GET_EXTRA_RESPONSES
}
