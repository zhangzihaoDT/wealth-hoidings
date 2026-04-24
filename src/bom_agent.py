import json
from typing import Any

from .bom_tools import build_bom_json


def bom_agent(target_url: str) -> dict[str, Any]:
    return build_bom_json(target_url)


def bom_agent_as_text(target_url: str) -> str:
    result = bom_agent(target_url)
    return json.dumps(result, ensure_ascii=False, indent=2)

