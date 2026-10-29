from src.api.utils.constants import PASSWORD_NOT_STRONG_MSG


class AppException(Exception):
    """Base exception of app"""

    status_code: int = 500
    detail: str = "Internal server error"
    headers: dict = None

    def __init__(self, detail: str = None, headers: dict = None, **kwargs):
        if detail is not None:
            self.detail = detail
        if headers is not None:
            self.headers = headers
        super().__init__(self.detail, self.headers)

        for key, value in kwargs.items():
            setattr(self, key, value)


class EmailAlreadyExistException(AppException):
    """Exception when trieng add new user with existing email 'status 400'"""

    status_code = 400
    detail = "Email already exist please choose another one"


class InvalidCredentialException(AppException):
    """Base Exception for provided data is invalid 'status 400'"""

    status_code = 400
    detail = "Invalid credentials"


class ConflictException(AppException):
    """Base Exception for conflict situations 'status 409'"""

    status_code = 409
    detail = "Conflict with third party service"


class PasswordNotStrongException(AppException):
    """
    Exception when user provides not strong
    password with special criteries 'status 400'
    """

    status_code = 400
    detail = PASSWORD_NOT_STRONG_MSG


class PasswordsDoNotMatchException(AppException):
    """Exception when trieng add new user and passwords not match 'status 400'"""

    status_code = 400
    detail = "Passwords don't match"


class BadRequestException(AppException):
    """Base bad request exception 'status 400'"""

    status_code = 400
    detail = "Bad Request"


class NotFoundException(AppException):
    """Base Exception when not found point 'status 404'"""

    status_code = 404
    detail = "Resource not found"


class PermissionDeniedException(AppException):
    """
    Base Exception fore user permission denied
    to do something need special role 'status 403'
    """

    status_code = 403
    detail = "Permission denied for complate this operation"


class UnauthorizedException(AppException):
    """Base Exception generated if token invalid or expires 'status 401'"""

    status_code = 401
    detail = "Unauthorized"


class InvalidOAuthStateException(AppException):
    """
    Social Auth Exception generated in user social auth
    if state lose or invalid 'status 400'
    """

    status_code = 400
    detail = "Authentication with social service fail"


class InvalidVerifyTokenException(AppException):
    """
    Email verification Exception generated if link
    and token expire or invalid 'status 403'
    """

    status_code = 403
    detail = "Token invalid or expire"


class NotVerifiedException(AppException):
    """Account is not verified Exception 'status 403'"""

    status_code = 403
    detail = "Account verification required"


class AccountIsNotActiveException(AppException):
    """Account is not activated Exception 'status 403'"""

    status_code = 403
    detail = "Account activation required"
