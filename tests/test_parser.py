import pytest

from src.errors import InvalidInputError
from src.parser import parse_invite_message


def test_parse_valid_invite_message():
    result = parse_invite_message("octocat - owner/repo")

    assert result.github_usernames == ["octocat"]
    assert result.github_username == "octocat"
    assert result.owner == "owner"
    assert result.repo == "repo"
    assert result.repo_full_name == "owner/repo"
    assert result.permission == "pull"
    assert result.telegram_username == ""


def test_parse_trims_whitespace():
    result = parse_invite_message("  github-user   -   owner/repository-name  ")

    assert result.github_usernames == ["github-user"]
    assert result.owner == "owner"
    assert result.repo == "repository-name"
    assert result.permission == "pull"
    assert result.telegram_username == ""


def test_parse_multiple_usernames():
    result = parse_invite_message("octocat,hubot - owner/repo")

    assert result.github_usernames == ["octocat", "hubot"]
    assert result.owner == "owner"
    assert result.repo == "repo"
    assert result.permission == "pull"


def test_parse_multiple_usernames_with_spaces():
    result = parse_invite_message("octocat , hubot , defunkt - owner/repo")

    assert result.github_usernames == ["octocat", "hubot", "defunkt"]


def test_parse_multiple_usernames_with_role():
    result = parse_invite_message("octocat,hubot - owner/repo - push")

    assert result.github_usernames == ["octocat", "hubot"]
    assert result.permission == "push"


def test_parse_multiple_usernames_with_telegram():
    result = parse_invite_message("@johndoe octocat,hubot - owner/repo")

    assert result.github_usernames == ["octocat", "hubot"]
    assert result.telegram_username == "johndoe"
    assert result.permission == "pull"


def test_parse_multiple_usernames_with_telegram_and_role():
    result = parse_invite_message("@johndoe octocat,hubot - owner/repo - push")

    assert result.github_usernames == ["octocat", "hubot"]
    assert result.telegram_username == "johndoe"
    assert result.permission == "push"


def test_parse_single_username_backward_compat():
    result = parse_invite_message("octocat - owner/repo")

    assert result.github_username == "octocat"
    assert result.github_usernames == ["octocat"]


def test_parse_with_explicit_role():
    result = parse_invite_message("octocat - owner/repo - push")

    assert result.github_username == "octocat"
    assert result.owner == "owner"
    assert result.repo == "repo"
    assert result.permission == "push"


def test_parse_with_role_case_insensitive():
    result = parse_invite_message("octocat - owner/repo - Push")

    assert result.permission == "push"


def test_parse_with_role_admin():
    result = parse_invite_message("octocat - owner/repo - admin")

    assert result.permission == "admin"


def test_parse_with_role_triage():
    result = parse_invite_message("octocat - owner/repo - triage")

    assert result.permission == "triage"


def test_parse_with_role_maintain():
    result = parse_invite_message("octocat - owner/repo - maintain")

    assert result.permission == "maintain"


def test_parse_with_telegram_username():
    result = parse_invite_message("@johndoe octocat - owner/repo")

    assert result.github_username == "octocat"
    assert result.owner == "owner"
    assert result.repo == "repo"
    assert result.permission == "pull"
    assert result.telegram_username == "johndoe"


def test_parse_with_telegram_and_role():
    result = parse_invite_message("@johndoe octocat - owner/repo - push")

    assert result.github_username == "octocat"
    assert result.owner == "owner"
    assert result.repo == "repo"
    assert result.permission == "push"
    assert result.telegram_username == "johndoe"


def test_parse_with_telegram_and_role_whitespace():
    result = parse_invite_message("  @johndoe   octocat   -   owner/repo   -   maintain  ")

    assert result.github_username == "octocat"
    assert result.owner == "owner"
    assert result.repo == "repo"
    assert result.permission == "maintain"
    assert result.telegram_username == "johndoe"


def test_parse_without_role_defaults_to_pull():
    result = parse_invite_message("octocat - owner/repo")

    assert result.permission == "pull"


def test_parse_rejects_invalid_role():
    with pytest.raises(InvalidInputError, match="Role khong hop le"):
        parse_invite_message("octocat - owner/repo - owner")


def test_parse_rejects_invalid_username_in_list():
    with pytest.raises(InvalidInputError, match="khong hop le"):
        parse_invite_message("octocat,bad_user - owner/repo")


@pytest.mark.parametrize(
    "message",
    [
        "",
        "octocat owner/repo",
        "-baduser - owner/repo",
        "baduser- - owner/repo",
        "bad_user - owner/repo",
        "octocat - owner",
        "octocat - /repo",
        "octocat - owner/",
        "octocat - owner/repo/extra",
        "octocat - https://github.com/owner/repo",
    ],
)
def test_parse_rejects_invalid_messages(message):
    with pytest.raises(InvalidInputError):
        parse_invite_message(message)
