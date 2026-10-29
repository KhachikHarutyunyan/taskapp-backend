from src.config.security import hash_password
from src.api.utils.dates_util import get_utc_date


BASE_PASSWORD = "Pass123456!"

REGISTER_USER = {
    "name": "monty",
    "email": "monty@mailbox.com",
    "password": BASE_PASSWORD,
    "confirm_password": BASE_PASSWORD,
}

WORKER_USER = {
    "name": "worker",
    "email": "worker@mailbox.com",
    "password": hash_password(BASE_PASSWORD),
    "verified_at": get_utc_date(),
    "is_active": True
}

ADMIN_USER = {
    "name": "admin",
    "email": "admin@mailbox.com",
    "password": hash_password(BASE_PASSWORD),
    "verified_at": get_utc_date(),
    "is_active": True
}

MANAGER_USER = {
    "name": "manager",
    "email": "manager@mailbox.com",
    "password": hash_password(BASE_PASSWORD),
    "verified_at": get_utc_date(),
    "is_active": True
}

INACTIVE_USER = {
    "name": "inactive",
    "email": "inactive@mailbox.com",
    "password": hash_password(BASE_PASSWORD),
    "verified_at": get_utc_date(),
    "is_active": False
}

UNVERIFIED_USER = {
    "name": "unverified",
    "email": "unverified@mailbox.com",
    "password": hash_password(BASE_PASSWORD),
    "verified_at": None,
    "is_active": True
}

NEW_USER = {
    "name": "unverified inactive",
    "email": "new@mailbox.com",
    "password": hash_password(BASE_PASSWORD),
    "verified_at": None,
    "is_active": False
}

NEW_TASK = {
    "name": "Today test task",
    "description": "Test description",
    "executors": []
}

TASKS_LIST = [
    {
        "name": "Today test task 1",
        "description": "Test description 1",
        "executors": []
    },
    {
        "name": "Today test task 2",
        "description": "Test description 2",
        "executors": []
    },
    {
        "name": "Today test task 3",
        "description": "Test description 3",
        "executors": []
    },
    {
        "name": "Today test task 4",
        "description": "Test description 4",
        "executors": []
    },
    {
        "name": "Today test task 5",
        "description": "Test description 5",
        "executors": []
    }
]