from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import orjson


def dumps(data: Any) -> str:
    return orjson.dumps(data, option=orjson.OPT_INDENT_2).decode()


def dump_to_file(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(data), encoding="utf-8")


def serialize_datetime(value: datetime) -> str:
    return value.astimezone().isoformat()

