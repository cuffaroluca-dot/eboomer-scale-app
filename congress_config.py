"""Configurazione URL e sessione congresso."""

import json
import socket
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "congress_settings.json"
DEFAULT_PORT = 8501
DEFAULT_PROFESSOR_IDS = [f"prof-{i:02d}" for i in range(1, 11)]


def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def load_settings() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(settings: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def get_base_url(port: int = DEFAULT_PORT) -> str:
    settings = load_settings()
    if settings.get("public_url"):
        return settings["public_url"].rstrip("/")
    return f"http://{get_local_ip()}:{port}"


def get_event_id() -> str:
    return load_settings().get("event_id", "congresso")


def set_event_id(event_id: str) -> None:
    s = load_settings()
    s["event_id"] = event_id.strip() or "congresso"
    save_settings(s)


def set_public_url(url: str) -> None:
    s = load_settings()
    s["public_url"] = url.strip().rstrip("/")
    save_settings(s)


def get_professor_ids() -> list[str]:
    ids = load_settings().get("professor_ids")
    if not isinstance(ids, list):
        return DEFAULT_PROFESSOR_IDS.copy()
    clean = [str(item).strip() for item in ids if str(item).strip()]
    return (clean + DEFAULT_PROFESSOR_IDS)[:10]


def set_professor_ids(professor_ids: list[str]) -> None:
    s = load_settings()
    clean = [item.strip() for item in professor_ids if item.strip()]
    s["professor_ids"] = (clean + DEFAULT_PROFESSOR_IDS)[:10]
    save_settings(s)


def participant_url(port: int = DEFAULT_PORT, source_id: str = "audience") -> str:
    event = get_event_id()
    return f"{get_base_url(port)}/?event={event}&source={source_id}"


def presenter_url(port: int = DEFAULT_PORT) -> str:
    return f"{get_base_url(port)}/?view=schermo"
