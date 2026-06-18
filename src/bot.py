import logging
import logging.handlers
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.config import AppConfig, load_config
from src.errors import AppError, ConfigError, InvalidInputError
from src.github_service import GitHubInvitationService
from src.parser import parse_invite_message

logger = logging.getLogger(__name__)

USAGE_TEXT = (
    "Gui loi moi GitHub bang format:\n"
    "  github_username - owner/repo\n"
    "  github_username - owner/repo - role\n"
    "  user1,user2,user3 - owner/repo\n"
    "  user1,user2 - owner/repo - role\n"
    "  @tele github_username - owner/repo\n"
    "  @tele user1,user2 - owner/repo - role\n\n"
    "Role hop le: pull (mac dinh), triage, push, maintain, admin\n"
    "Vi du:\n"
    "  octocat - owner/repository-name\n"
    "  octocat,hubot - owner/repository-name - push\n"
    "  @johndoe octocat - owner/repository-name - push"
)


class BotServices:
    def __init__(
        self,
        config: AppConfig,
        github_service: GitHubInvitationService,
    ):
        self.config = config
        self.github_service = github_service


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_text(USAGE_TEXT)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_chat is None:
        return

    services = _get_services(context)

    if not is_update_allowed(update, services.config):
        await update.message.reply_text("Ban khong co quyen su dung bot nay.")
        return

    try:
        invite_request = parse_invite_message(update.message.text or "")
    except InvalidInputError:
        await update.message.reply_text(
            "Sai format. Hay nhap:\n"
            "  github_username - owner/repo\n"
            "  user1,user2 - owner/repo\n"
            "  github_username - owner/repo - role\n"
            "  @tele user1,user2 - owner/repo - role\n\n"
            "Vi du: octocat - owner/repository-name"
        )
        return

    tele_info = ""
    if invite_request.telegram_username:
        tele_info = f" (Telegram: @{invite_request.telegram_username})"

    role_info = f" voi role {invite_request.permission}"

    succeeded: list[str] = []
    failed: list[tuple[str, str]] = []

    for username in invite_request.github_usernames:
        try:
            result = services.github_service.invite_collaborator(
                invite_request.owner,
                invite_request.repo,
                username,
                permission=invite_request.permission,
            )
            if result.status == "invited":
                succeeded.append(f"✅ {username}: Da gui loi moi")
            else:
                succeeded.append(f"✅ {username}: Da co quyen hoac quyen da duoc cap nhat")
        except AppError as exc:
            failed.append((username, exc.message))
            logger.error(
                "Invite FAILED | user=%s | repo=%s | role=%s | tele=%s | error=%s",
                username,
                invite_request.repo_full_name,
                invite_request.permission,
                invite_request.telegram_username or "N/A",
                exc.message,
            )

    lines: list[str] = []
    lines.append(f"Ket qua moi vao repo {invite_request.repo_full_name}{role_info}:{tele_info}")

    for msg in succeeded:
        lines.append(msg)

    for username, error_msg in failed:
        lines.append(f"❌ {username}: {error_msg}")

    await update.message.reply_text("\n".join(lines))


def build_services(config: AppConfig) -> BotServices:
    github_service = GitHubInvitationService(
        token=config.github_token,
        api_version=config.github_api_version,
        default_permission=config.default_permission,
    )
    return BotServices(config, github_service)


def build_application(config: AppConfig, services: BotServices) -> Application:
    application = Application.builder().token(config.telegram_bot_token).build()
    application.bot_data["services"] = services
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return application


def is_update_allowed(update: Update, config: AppConfig) -> bool:
    chat_id = update.effective_chat.id if update.effective_chat is not None else None
    user_id = update.effective_user.id if update.effective_user is not None else None

    chat_allowed = chat_id is not None and chat_id in config.allowed_telegram_chat_ids
    user_allowed = user_id is not None and user_id in config.allowed_telegram_user_ids

    return chat_allowed or user_allowed


def _get_services(context: ContextTypes.DEFAULT_TYPE) -> BotServices:
    services = context.application.bot_data.get("services")
    if not isinstance(services, BotServices):
        raise ConfigError("Bot services chua duoc khoi tao.")
    return services


def _setup_logging(config: AppConfig) -> None:
    """Configure root logger with both console and file handlers."""
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    log_format = "%(asctime)s %(levelname)s %(name)s: %(message)s"

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)

    # File handler — auto-rotates at midnight, names files bot_YYYY-MM-DD.log
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "bot.log")

    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, 
        when="D", 
        interval=config.log_rotation_interval_days, 
        backupCount=config.log_backup_count, 
        encoding="utf-8",
    )

    # Custom namer: bot.log.2026-06-18 → bot_2026-06-18.log
    def log_namer(default_name: str) -> str:
        # default_name = "/path/logs/bot.log.2026-06-18"
        base, ext = default_name.rsplit(".", 1)  # ext = "2026-06-18"
        directory = os.path.dirname(base)
        return os.path.join(directory, f"bot_{ext}.log")

    def log_rotator(source: str, dest: str) -> None:
        if os.path.exists(source):
            os.rename(source, dest)

    file_handler.suffix = "%Y-%m-%d"
    file_handler.namer = log_namer
    file_handler.rotator = log_rotator
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(file_handler)


def main() -> None:
    config = load_config()
    _setup_logging(config)
    logger.info("Bot starting...")
    application = build_application(config, build_services(config))
    application.run_polling()


if __name__ == "__main__":
    main()
