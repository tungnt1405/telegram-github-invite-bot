import pytest

from src.config import load_config_from_env
from src.errors import ConfigError


def valid_env():
    return {
        "TELEGRAM_BOT_TOKEN": "telegram-token",
        "GITHUB_TOKEN": "github-token",
        "ALLOWED_TELEGRAM_CHAT_IDS": "-1001234567890, -1009876543210",
    }


def test_load_config_uses_defaults():
    config = load_config_from_env(valid_env())

    assert config.telegram_bot_token == "telegram-token"
    assert config.github_token == "github-token"
    assert config.allowed_telegram_chat_ids == {-1001234567890, -1009876543210}
    assert config.allowed_telegram_user_ids == set()
    assert config.default_permission == "pull"
    assert config.github_api_version == "2022-11-28"
    assert config.log_level == "INFO"
    assert config.log_backup_count == 30
    assert config.log_rotation_interval_days == 1


def test_load_config_accepts_custom_values():
    env = valid_env() | {
        "DEFAULT_PERMISSION": "push",
        "GITHUB_API_VERSION": "2023-01-01",
        "LOG_LEVEL": "DEBUG",
        "LOG_BACKUP_COUNT": "5",
        "LOG_ROTATION_INTERVAL_DAYS": "7",
    }

    config = load_config_from_env(env)

    assert config.default_permission == "push"
    assert config.github_api_version == "2023-01-01"
    assert config.log_level == "DEBUG"
    assert config.log_backup_count == 5
    assert config.log_rotation_interval_days == 7


def test_load_config_with_user_ids_only():
    env = {
        "TELEGRAM_BOT_TOKEN": "telegram-token",
        "GITHUB_TOKEN": "github-token",
        "ALLOWED_TELEGRAM_USER_IDS": "123,456",
    }

    config = load_config_from_env(env)

    assert config.allowed_telegram_chat_ids == set()
    assert config.allowed_telegram_user_ids == {123, 456}


def test_load_config_with_single_user_id():
    env = {
        "TELEGRAM_BOT_TOKEN": "telegram-token",
        "GITHUB_TOKEN": "github-token",
        "ALLOWED_TELEGRAM_USER_IDS": "123",
    }

    config = load_config_from_env(env)

    assert config.allowed_telegram_user_ids == {123}


def test_load_config_with_both_chat_and_user_ids():
    env = valid_env() | {
        "ALLOWED_TELEGRAM_USER_IDS": "111,222",
    }

    config = load_config_from_env(env)

    assert config.allowed_telegram_chat_ids == {-1001234567890, -1009876543210}
    assert config.allowed_telegram_user_ids == {111, 222}


def test_load_config_rejects_no_chat_or_user_ids():
    env = {
        "TELEGRAM_BOT_TOKEN": "telegram-token",
        "GITHUB_TOKEN": "github-token",
    }

    with pytest.raises(ConfigError, match="ALLOWED_TELEGRAM_CHAT_IDS hoac ALLOWED_TELEGRAM_USER_IDS"):
        load_config_from_env(env)


@pytest.mark.parametrize("missing_key", ["TELEGRAM_BOT_TOKEN", "GITHUB_TOKEN"])
def test_load_config_requires_required_values(missing_key):
    env = valid_env()
    env[missing_key] = ""

    with pytest.raises(ConfigError):
        load_config_from_env(env)


def test_load_config_rejects_invalid_allowed_chat_id():
    env = valid_env() | {"ALLOWED_TELEGRAM_CHAT_IDS": "-100123,abc"}

    with pytest.raises(ConfigError):
        load_config_from_env(env)


def test_load_config_rejects_invalid_user_id():
    env = valid_env() | {"ALLOWED_TELEGRAM_USER_IDS": "123,abc"}

    with pytest.raises(ConfigError):
        load_config_from_env(env)


def test_load_config_rejects_empty_allowed_chat_ids():
    env = {
        "TELEGRAM_BOT_TOKEN": "telegram-token",
        "GITHUB_TOKEN": "github-token",
        "ALLOWED_TELEGRAM_CHAT_IDS": "",
    }

    with pytest.raises(ConfigError):
        load_config_from_env(env)


def test_load_config_rejects_invalid_permission():
    env = valid_env() | {"DEFAULT_PERMISSION": "owner"}

    with pytest.raises(ConfigError):
        load_config_from_env(env)


def test_load_config_rejects_invalid_log_backup_count():
    env = valid_env() | {"LOG_BACKUP_COUNT": "abc"}

    with pytest.raises(ConfigError, match="phai la so nguyen"):
        load_config_from_env(env)


def test_load_config_rejects_invalid_log_rotation_interval():
    env = valid_env() | {"LOG_ROTATION_INTERVAL_DAYS": "abc"}

    with pytest.raises(ConfigError, match="phai la so nguyen"):
        load_config_from_env(env)
