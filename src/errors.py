class AppError(Exception):
    """Base application error with a user-safe message."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidInputError(AppError):
    pass


class ConfigError(AppError):
    pass


class GitHubInvitationError(AppError):
    pass
