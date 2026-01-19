from dataclasses import dataclass, field
from typing import Any


STATE_IDLE = "idle"
STATE_WAIT_SONG = "wait_song"
STATE_WAIT_WHATSAPP_CONTACT = "wait_whatsapp_contact"
STATE_WAIT_WHATSAPP_MESSAGE = "wait_whatsapp_message"
STATE_WAIT_WHATSAPP_CONFIRM = "wait_whatsapp_confirm"
STATE_WAIT_PC_CONFIRM = "wait_pc_confirm"
STATE_WAIT_REMINDER_TIME = "wait_reminder_time"


@dataclass
class AssistantState:
    is_active: bool = False
    last_activation_ts: float = 0.0
    activation_timeout: int = 30
    current_state: str = STATE_IDLE
    silent_mode: bool = False
    debug_mode: bool = False
    safe_mode: bool = False
    confirmation_code: str = "codigo seguro"
    pending: dict[str, Any] = field(default_factory=dict)
    memory: dict[str, Any] = field(default_factory=lambda: {
        "last_action": None,
        "last_response": "",
        "last_song": "",
        "last_contact": "",
        "last_message": "",
    })

    def set_last_action(self, action_type: str, payload: dict[str, Any] | None = None):
        self.memory["last_action"] = {
            "type": action_type,
            "payload": payload or {},
        }
