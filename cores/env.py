from dotenv import dotenv_values
from pathlib import Path


def get_env() -> dict[str, str | None]:
<<<<<<< HEAD:cores/env.py
    env_file: Path = (Path(__file__).resolve(strict=True).parent / "cfg.env")
=======
    env_file = (Path(__file__).resolve(strict=True).parent / "cosmic_cfg.env")
>>>>>>> ba1a3fe (doc: update README to finalise last migration step to new repo):backend/cores/env.py

    return dotenv_values(
        dotenv_path=env_file,
        encoding= "utf-8"
    )
