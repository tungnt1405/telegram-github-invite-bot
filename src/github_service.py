from dataclasses import dataclass

import requests

from src.errors import GitHubInvitationError


@dataclass(frozen=True)
class InvitationResult:
    status: str
    message: str


class GitHubInvitationService:
    def __init__(
        self,
        token: str,
        api_version: str,
        default_permission: str,
        session: requests.Session | None = None,
    ):
        self._token = token
        self._api_version = api_version
        self._default_permission = default_permission
        self._session = session or requests.Session()

    def invite_collaborator(
        self, owner: str, repo: str, username: str, permission: str | None = None,
    ) -> InvitationResult:
        url = f"https://api.github.com/repos/{owner}/{repo}/collaborators/{username}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": self._api_version,
        }
        effective_permission = permission or self._default_permission
        payload = {"permission": effective_permission}

        try:
            response = self._session.put(url, headers=headers, json=payload, timeout=15)
        except requests.Timeout as exc:
            raise GitHubInvitationError("Ket noi GitHub bi timeout. Hay thu lai sau.") from exc
        except requests.RequestException as exc:
            raise GitHubInvitationError("Khong the ket noi GitHub. Hay kiem tra mang hoac thu lai sau.") from exc

        if response.status_code == 201:
            return InvitationResult("invited", "Da gui loi moi GitHub.")
        if response.status_code == 204:
            return InvitationResult("already_added", "User da co quyen hoac quyen da duoc cap nhat.")
        if response.status_code == 403:
            raise GitHubInvitationError(
                "Khong the gui loi moi. GitHub token co the thieu quyen admin/write cho repo "
                "hoac policy cua repo/org dang chan invite."
            )
        if response.status_code == 404:
            raise GitHubInvitationError("Khong tim thay repo/user hoac GitHub token khong co quyen truy cap repo nay.")
        if response.status_code == 422:
            raise GitHubInvitationError(
                "GitHub tu choi request. Username, permission hoac gioi han invite co the khong hop le."
            )

        raise GitHubInvitationError(f"GitHub API loi voi ma trang thai {response.status_code}.")
