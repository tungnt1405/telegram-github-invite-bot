from dataclasses import dataclass
import re

from src.errors import InvalidInputError


USAGE_MESSAGE = "Sai format. Hay nhap: github_username - owner/repo"
USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
REPO_PART_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
VALID_PERMISSIONS = {"pull", "triage", "push", "maintain", "admin"}

# Matches:
#   username - owner/repo
#   username - owner/repo - role
#   user1,user2 - owner/repo
#   user1,user2 - owner/repo - role
#   @tele username - owner/repo
#   @tele user1,user2 - owner/repo - role
MESSAGE_RE = re.compile(
    r"^\s*"
    r"(?:@(?P<telegram>\S+)\s+)?"
    r"(?P<usernames>.+?)\s+-\s+(?P<repo>.+?)"
    r"(?:\s+-\s+(?P<role>[A-Za-z]+))?"
    r"\s*$"
)

DEFAULT_PERMISSION = "pull"


@dataclass(frozen=True)
class InviteRequest:
    github_usernames: list[str]
    owner: str
    repo: str
    permission: str
    telegram_username: str

    @property
    def repo_full_name(self) -> str:
        return f"{self.owner}/{self.repo}"

    @property
    def github_username(self) -> str:
        """Backward-compatible: return first username."""
        return self.github_usernames[0] if self.github_usernames else ""


def parse_invite_message(message: str) -> InviteRequest:
    if not message or not message.strip():
        raise InvalidInputError(USAGE_MESSAGE)

    match = MESSAGE_RE.match(message)
    if not match:
        raise InvalidInputError(USAGE_MESSAGE)

    usernames_text = match.group("usernames").strip()
    repo_text = match.group("repo").strip()
    role_text = match.group("role")
    telegram_text = match.group("telegram")

    # Parse comma-separated usernames
    raw_usernames = [u.strip() for u in usernames_text.split(",")]
    github_usernames = [u for u in raw_usernames if u]

    if not github_usernames:
        raise InvalidInputError("GitHub username khong hop le.")

    for username in github_usernames:
        if not USERNAME_RE.match(username):
            raise InvalidInputError(f"GitHub username khong hop le: {username}")

    if repo_text.startswith("http://") or repo_text.startswith("https://"):
        raise InvalidInputError("Repo khong hop le. Hay nhap theo dang owner/repo.")

    repo_parts = repo_text.split("/")
    if len(repo_parts) != 2:
        raise InvalidInputError("Repo khong hop le. Hay nhap theo dang owner/repo.")

    owner = repo_parts[0].strip()
    repo = repo_parts[1].strip()

    if not owner or not repo:
        raise InvalidInputError("Repo khong hop le. Hay nhap theo dang owner/repo.")

    if not REPO_PART_RE.match(owner) or not REPO_PART_RE.match(repo):
        raise InvalidInputError("Repo khong hop le. Hay nhap theo dang owner/repo.")

    permission = DEFAULT_PERMISSION
    if role_text:
        permission = role_text.strip().lower()
        if permission not in VALID_PERMISSIONS:
            raise InvalidInputError(
                "Role khong hop le. Gia tri hop le: pull, triage, push, maintain, admin."
            )

    telegram_username = ""
    if telegram_text:
        telegram_username = telegram_text.strip()

    return InviteRequest(
        github_usernames=github_usernames,
        owner=owner,
        repo=repo,
        permission=permission,
        telegram_username=telegram_username,
    )
