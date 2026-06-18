from unittest.mock import Mock

import pytest
import requests

from src.errors import GitHubInvitationError
from src.github_service import GitHubInvitationService


def make_service(response=None, side_effect=None):
    session = Mock()
    session.put = Mock(return_value=response, side_effect=side_effect)
    return GitHubInvitationService("token", "2022-11-28", "pull", session=session), session


def response(status_code):
    mocked = Mock()
    mocked.status_code = status_code
    return mocked


def test_invite_collaborator_maps_201_to_invited():
    service, session = make_service(response(201))

    result = service.invite_collaborator("owner", "repo", "octocat")

    assert result.status == "invited"
    assert result.message == "Da gui loi moi GitHub."
    session.put.assert_called_once_with(
        "https://api.github.com/repos/owner/repo/collaborators/octocat",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer token",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"permission": "pull"},
        timeout=15,
    )


def test_invite_collaborator_uses_default_permission_when_none():
    service, session = make_service(response(201))

    service.invite_collaborator("owner", "repo", "octocat", permission=None)

    session.put.assert_called_once()
    call_kwargs = session.put.call_args
    assert call_kwargs.kwargs["json"] == {"permission": "pull"}


def test_invite_collaborator_uses_explicit_permission():
    service, session = make_service(response(201))

    service.invite_collaborator("owner", "repo", "octocat", permission="push")

    session.put.assert_called_once()
    call_kwargs = session.put.call_args
    assert call_kwargs.kwargs["json"] == {"permission": "push"}


def test_invite_collaborator_uses_admin_permission():
    service, session = make_service(response(201))

    service.invite_collaborator("owner", "repo", "octocat", permission="admin")

    session.put.assert_called_once()
    call_kwargs = session.put.call_args
    assert call_kwargs.kwargs["json"] == {"permission": "admin"}


def test_invite_collaborator_maps_204_to_already_added():
    service, _ = make_service(response(204))

    result = service.invite_collaborator("owner", "repo", "octocat")

    assert result.status == "already_added"


@pytest.mark.parametrize("status_code", [403, 404, 422, 500])
def test_invite_collaborator_maps_error_statuses(status_code):
    service, _ = make_service(response(status_code))

    with pytest.raises(GitHubInvitationError):
        service.invite_collaborator("owner", "repo", "octocat")


def test_invite_collaborator_maps_timeout():
    service, _ = make_service(side_effect=requests.Timeout())

    with pytest.raises(GitHubInvitationError):
        service.invite_collaborator("owner", "repo", "octocat")


def test_invite_collaborator_maps_network_error():
    service, _ = make_service(side_effect=requests.RequestException())

    with pytest.raises(GitHubInvitationError):
        service.invite_collaborator("owner", "repo", "octocat")
