from dataclasses import dataclass, field
import os

from dotenv import load_dotenv

from src.errors import ConfigError


VALID_PERMISSIONS = {"pull", "triage", "push", "maintain", "admin"}


@dataclass(frozen=True)
class AppConfig:
    telegram_bot_token: str
    github_token: str
    allowed_telegram_chat_ids: set[int]
    allowed_telegram_user_ids: set[int]
    default_permission: str
    github_api_version: str
    log_level: str
    log_backup_count: int
    log_rotation_interval_days: int


def load_config() -> AppConfig:
    load_dotenv()
    return load_config_from_env(os.environ)


def load_config_from_env(env: dict[str, str]) -> AppConfig:
    telegram_bot_token = _required(env, "TELEGRAM_BOT_TOKEN")
    github_token = _required(env, "GITHUB_TOKEN")

    # At least one of ALLOWED_TELEGRAM_CHAT_IDS or ALLOWED_TELEGRAM_USER_IDS must be set
    raw_chat_ids = env.get("ALLOWED_TELEGRAM_CHAT_IDS", "").strip()
    raw_user_ids = env.get("ALLOWED_TELEGRAM_USER_IDS", "").strip()

    if not raw_chat_ids and not raw_user_ids:
        raise ConfigError(
            "Phai cau hinh it nhat ALLOWED_TELEGRAM_CHAT_IDS hoac ALLOWED_TELEGRAM_USER_IDS."
        )

    allowed_chat_ids: set[int] = set()
    if raw_chat_ids:
        allowed_chat_ids = _parse_id_set(raw_chat_ids, "ALLOWED_TELEGRAM_CHAT_IDS")

    allowed_user_ids: set[int] = set()
    if raw_user_ids:
        allowed_user_ids = _parse_id_set(raw_user_ids, "ALLOWED_TELEGRAM_USER_IDS")

    default_permission = env.get("DEFAULT_PERMISSION", "pull").strip().lower()

    if default_permission not in VALID_PERMISSIONS:
        raise ConfigError(
            "DEFAULT_PERMISSION khong hop le. Gia tri hop le: pull, triage, push, maintain, admin."
        )

    log_backup_count = _parse_int(env, "LOG_BACKUP_COUNT", 30)
    log_rotation_interval_days = _parse_int(env, "LOG_ROTATION_INTERVAL_DAYS", 1)

    return AppConfig(
        telegram_bot_token=telegram_bot_token,
        github_token=github_token,
        allowed_telegram_chat_ids=allowed_chat_ids,
        allowed_telegram_user_ids=allowed_user_ids,
        default_permission=default_permission,
        github_api_version=env.get("GITHUB_API_VERSION", "2022-11-28").strip() or "2022-11-28",
        log_level=env.get("LOG_LEVEL", "INFO").strip() or "INFO",
        log_backup_count=log_backup_count,
        log_rotation_interval_days=log_rotation_interval_days,
    )


def _required(env: dict[str, str], name: str) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise ConfigError(f"Thieu bien moi truong bat buoc: {name}.")
    return value


def _parse_id_set(value: str, env_name: str) -> set[int]:
    ids: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            ids.add(int(item))
        except ValueError as exc:
            raise ConfigError(f"{env_name} phai la danh sach so, cach nhau bang dau phay.") from exc

    if not ids:
        raise ConfigError(f"{env_name} khong duoc rong.")
    return ids


def _parse_int(env: dict[str, str], name: str, default: int) -> int:
    val_str = env.get(name, "").strip()
    if not val_str:
        return default
    try:
        return int(val_str)
    except ValueError as exc:
        raise ConfigError(f"{name} phai la so nguyen.") from exc
