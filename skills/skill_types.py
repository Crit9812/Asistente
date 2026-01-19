from dataclasses import dataclass
from typing import Any


@dataclass
class SkillResult:
    handled: bool
    response: str | None = None
    end_session: bool = False
    detected_intent: str | None = None
    data: dict[str, Any] | None = None
