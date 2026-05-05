### Core modules ###
from fastapi import (
    HTTPException,
    status
)
from httpx import (
    AsyncClient,
    ConnectError,
    ConnectTimeout,
    Response
)


### Type hints ###
from typing import Any


### Internal modules ###
from ..cores.globals import LLM_ROLE



async def get_role_name(
    # TODO: util to dynamically check for valid endpoint format
    endpoint:   str     = "http://localhost:8000/api/v1/roles/",
    lifetime:   float   = 10.0,
    verbose:    bool    = False
) -> list[str]:
    """
    Retrieve role names from the Roles API endpoint.

    This helper function fetches roles data from the specified endpoint and
    returns a list of role names.

    Args:
        endpoint: Base URL of the Roles API endpoint.
            Defaults to "http://localhost:8000/api/v1/roles/".
        lifetime: HTTP client timeout in seconds.
            Defaults to 10.0 seconds.
        verbose: Enable debug output of roles data.
            When True, prints formatted roles data.

    Returns:
        List of role names.
        Example: ['admin', 'user']

    Raises:
        HTTPException: With status code 500 if any connection error occurs
            (ConnectError, ConnectTimeout) or other unexpected exceptions.

    Example:
        >>> roles = get_roles_name(verbose=True)
        >>> roles[0]  # First role name
        'admin'
    """
    names: list[str] = []

    if endpoint.find("localhost") == -1:
        # No need to provide the container name when calling API endpoint within
        # the same container
        if verbose:
            print(
                "{debug_msg:s}{debug_data:s}".format(
                    debug_msg="{0:s}{1:s}".format(
                        "Calling API endpoints within the same container doesn't require the server to know which container name it is calling from.",
                        "Please modify the endpoint to use 'localhost' instead.",
                    ),
                    debug_data=f"Received: {endpoint}"
                )
            )
            return names

        else:
            return names

    else:
        async with AsyncClient(
            base_url=endpoint,
            timeout=lifetime
        ) as client:
            try:
                response: Response = await client.get(url="/")
                data: list[dict[str, Any]] = response.json()["result"]

                if len(data) == 0:
                    # No roles name available
                    if verbose:
                        print(
                            "{head_sep:s}\n{body_msg:s}\n{foot_sep:s}".format(
                                head_sep=f"{'=' * 80}",
                                body_msg="[DEBUG]   ROLES DATA ('NAME' ONLY)   [DEBUG]",
                                foot_sep=f"{'=' * 80}"
                            )
                        )
                        print(
                            "{debug_msg:s}\n{foot_sep:s}".format(
                                debug_msg="No roles name available...",
                                foot_sep=f"{'=' * 80}"
                            )
                        )
                        return names

                    else:
                        return names

                else:
                    # There is/are roles name available
                    names.extend([
                        value
                        for role_data in data
                        for (key, value) in role_data.items()
                        if "name" in key
                    ])

                    if verbose:
                        print(
                            "{head_sep:s}\n{body_msg:s}\n{foot_sep:s}".format(
                                head_sep=f"{'=' * 80}",
                                body_msg="[DEBUG]   ROLES DATA ('NAME' ONLY)   [DEBUG]",
                                foot_sep=f"{'=' * 80}"
                            )
                        )
                        print(
                            "{debug_msg:s}\n{foot_sep:s}".format(
                                debug_msg=f"{names}",
                                foot_sep=f"{'=' * 80}"
                            )
                        )
                        return names

                    else:
                        return names


            except ConnectError as httpx_err:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"{httpx_err}"
                    )


            except ConnectTimeout as httpx_err:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"{httpx_err}"
                )


async def valid_role_name(
    chat_history_data:  list[dict[str, Any]],
    verbose:            bool = False
) -> bool:
    """
    Validate role names in chat history data against role names in the database
    (fetched from Roles API endpoint).

    Args:
        chat_history_data:
            List of chat history dictionaries containing 'user_role' and
            'llm_role' keys.
        verbose: Enable debug output of validation failures/successes.
            When True, prints formatted validation debug message.

    Returns:
        True if all role names are valid, False otherwise.
    """
    if verbose:
        roles_name: list[str] = await get_role_name(verbose=True)

        # NOTE: these 2 vars are for type-hint purposes
        admin_role_name:    str
        normal_role_name:   str
        (admin_role_name, normal_role_name) = roles_name

        for chat_history in chat_history_data:
            if "user_role" not in chat_history:
                print(
                    "{head_sep:s}\n{body_msg:s}\n{foot_sep:s}".format(
                        head_sep=f"{'=' * 80}",
                        body_msg="[DEBUG]   ROLES DATA ('NAME' ONLY)   [DEBUG]",
                        foot_sep=f"{'=' * 80}"
                    )
                )
                print(
                    "{debug_msg:s}\n{foot_sep:s}".format(
                        debug_msg="{trig:s}: {cond:s}".format(
                            trig="Chatbox update forbidden",
                            cond="Missing 'user_role' key in chat history data"
                        ),
                        foot_sep=f"{'=' * 80}"
                    )
                )
                return False

            if "llm_role" not in chat_history:
                print(
                    "{head_sep:s}\n{body_msg:s}\n{foot_sep:s}".format(
                        head_sep=f"{'=' * 80}",
                        body_msg="[DEBUG]   ROLES DATA ('NAME' ONLY)   [DEBUG]",
                        foot_sep=f"{'=' * 80}"
                    )
                )
                print(
                    "{debug_msg:s}\n{foot_sep:s}".format(
                        debug_msg="{trig:s}: {cond:s}".format(
                            trig="Chatbox update forbidden",
                            cond="Missing 'llm_role' key in chat history data"
                        ),
                        foot_sep=f"{'=' * 80}"
                    )
                )
                return False

            user_chat_history_role: str = chat_history["user_role"]
            llm_chat_history_role:  str = chat_history["llm_role"]

            if user_chat_history_role not in (admin_role_name, normal_role_name):
                # Invalid user role in chat history
                print(
                    "{head_sep:s}\n{body_msg:s}\n{foot_sep:s}".format(
                        head_sep=f"{'=' * 80}",
                        body_msg="[DEBUG]   ROLES DATA ('NAME' ONLY)   [DEBUG]",
                        foot_sep=f"{'=' * 80}"
                    )
                )
                print(
                    "{debug_msg:s}\n{foot_sep:s}".format(
                        debug_msg="{trig:s}: {cond:s}".format(
                            trig="Chatbox update forbidden",
                            cond=f"User role value must be either 'admin' or 'user' only (lowercase convention). Received: {user_chat_history_role}"
                        ),
                        foot_sep=f"{'=' * 80}"
                    )
                )
                return False

            if llm_chat_history_role != LLM_ROLE:
                # Invalid LLM role in chat history
                print(
                    "{head_sep:s}\n{body_msg:s}\n{foot_sep:s}".format(
                        head_sep=f"{'=' * 80}",
                        body_msg="[DEBUG]   ROLES DATA ('NAME' ONLY)   [DEBUG]",
                        foot_sep=f"{'=' * 80}"
                    )
                )
                print(
                    "{debug_msg:s}\n{foot_sep:s}".format(
                        debug_msg="{trig:s}: {cond:s}".format(
                            trig="Chatbox update forbidden",
                            cond=f"LLM role value must be 'assistant' only (lowercase convention). Received: {llm_chat_history_role}"
                        ),
                        foot_sep=f"{'=' * 80}"
                    )
                )
                return False

        # Valid roles in chat history
        return True

    else:
        roles_name: list[str] = await get_role_name()

        # NOTE: these 2 vars are for type-hint purposes
        admin_role_name:    str
        normal_role_name:   str
        (admin_role_name, normal_role_name) = roles_name

        for chat_history in chat_history_data:
            if "user_role" not in chat_history:
                return False

            if "llm_role" not in chat_history:
                return False

            user_chat_history_role: str = chat_history["user_role"]
            llm_chat_history_role:  str = chat_history["llm_role"]

            if user_chat_history_role not in (admin_role_name, normal_role_name):
                # Invalid user role in chat history
                return False

            if llm_chat_history_role != LLM_ROLE:
                # Invalid LLM role in chat history
                return False

        # Valid roles in chat history
        return True
