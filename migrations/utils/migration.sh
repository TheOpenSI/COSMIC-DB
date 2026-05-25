#!/bin/sh

.venv/bin/alembic upgrade head
uv run fastapi dev --host 0.0.0.0
