# Telegram GitHub Invitation Bot

Python Telegram bot that accepts a GitHub username:

```text
github_username - owner/repo
github_username - owner/repo - role
@telegram_handle github_username - owner/repo
@telegram_handle github_username - owner/repo - role
```

The bot calls the GitHub REST API to invite that GitHub user (or multiple users) as a repository collaborator, and logs the result.

If no role is specified, the default is `pull` (read-only / guest). You can override the role per invite by appending `- role` to the message:

| Role | Description |
|------|-------------|
| `pull` | Read-only (mặc định / guest) |
| `triage` | Triage issues and pull requests |
| `push` | Read and write |
| `maintain` | Maintain the repository |
| `admin` | Full admin access |

> **Note:** Specifying a role (`pull`, `triage`, `push`, `maintain`, `admin`) only applies to Organization/Enterprise repositories. For personal repositories (both public and private), GitHub does not support fine-grained roles and only grants a single universal Collaborator permission.

Optionally prefix the message with `@telegram_handle` to log who requested the invite.

GitHub personal accounts do not support inviting collaborators directly by email through the public REST API. The official API requires the GitHub username.

Vietnamese deployment guide: [docs/huong-dan-trien-khai.md](docs/huong-dan-trien-khai.md)

## Setup

1. Create a Telegram bot with BotFather and copy the bot token.
2. Add the bot to the Telegram group that is allowed to use it.
3. Get the Telegram group chat ID.
4. Create a GitHub fine-grained personal access token.
5. Grant the token access to the repositories you want to manage.
6. Grant repository permission `Administration: write`.
7. Create a local environment file:

```bash
copy .env.example .env
```

7. Fill in `.env`:

```env
TELEGRAM_BOT_TOKEN=your-telegram-token
GITHUB_TOKEN=your-github-token
ALLOWED_TELEGRAM_CHAT_IDS=-1001234567890
ALLOWED_TELEGRAM_USER_IDS=
DEFAULT_PERMISSION=pull
GITHUB_API_VERSION=2022-11-28
LOG_LEVEL=INFO
LOG_BACKUP_COUNT=30
LOG_ROTATION_INTERVAL_DAYS=1
```

- `ALLOWED_TELEGRAM_CHAT_IDS`: List of group/chat IDs.
- `ALLOWED_TELEGRAM_USER_IDS`: List of individual user IDs.
The bot accepts invite commands if the message originates from either an allowed chat or an allowed user.

- `LOG_BACKUP_COUNT`: Number of old log files to keep (default 30). Set to 0 to keep all.
- `LOG_ROTATION_INTERVAL_DAYS`: Number of days between log rotation/cleanup (default 1).

## Install

Use a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```bash
.\.venv\Scripts\python.exe -m src.bot
```

Then send the bot a message:

```text
octocat - owner/repository-name
```

This invites `octocat` with the default `pull` (guest) role.

To invite multiple users at once, separate usernames by comma:

```text
user1,user2,user3 - owner/repository-name
```

To specify a role explicitly:

```text
octocat - owner/repository-name - push
```

To also log who requested the invite:

```text
@johndoe octocat - owner/repository-name - push
```

## Docker

Build and run with Docker Compose:

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f github-invite-bot
```

Stop:

```bash
docker compose down
```

The container reads secrets from `.env`. Do not bake tokens into the image.
Do not share `docker compose config` output when using a real `.env`, because it can print resolved secrets.

## Test

```bash
.\.venv\Scripts\python.exe -m pytest -v
```

## Security Notes

- Do not commit `.env`.
- Keep Telegram and GitHub tokens private.
- Only Telegram users or group chats in `ALLOWED_TELEGRAM_USER_IDS` or `ALLOWED_TELEGRAM_CHAT_IDS` can use the bot.
- Default GitHub collaborator permission is `pull` (guest / read-only).
- The app does not log tokens or raw authorization headers.
