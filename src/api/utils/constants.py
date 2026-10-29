from enum import Enum


class Roles(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    WORKER = "worker"


LIMITS = {"auth": "10/minute", "api": "200/minute", "admin": "30/minute"}

ORIGINS = ["http://taskapp.local:30080", "http://taskapp.dev.local:30080", "http://taskapp.stage.local:30080", "http://taskapp.local"]

VERIFY_KEY = "verify_account"
FORGOT_PWD_KEY = "forgot_password"

SPECIAL_CHARACTERS = ["@", "!", "#", "$", "%", "=", ":", "?", ".", "/", "|", "~", ">"]

PASSWORD_NOT_STRONG_MSG = f"Password must contain at least one number \
    and one uppercase and lowercase letter and one of special characters \
    '{SPECIAL_CHARACTERS}', and at least 8 or more characters."
