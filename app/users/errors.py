from app.shared.errors import DomainError


class UserNotFound(DomainError):
    pass


class EmailAlreadyExists(DomainError):
    pass


class UsernameAlreadyExists(DomainError):
    pass
