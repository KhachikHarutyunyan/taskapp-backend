from src.config.security import hash_password

BASE_PASSWORD = "Pass123456!"

REGISTER_USER = {
    "name": "monty",
    "email": "monty@mailbox.com",
    "password": BASE_PASSWORD,
    "confirm_password": BASE_PASSWORD,
}

ADMIN_USER = {
    "name": "admin",
    "email": "admin@mailbox.com",
    "password": hash_password(BASE_PASSWORD),
}

MANAGER_USER = {
    "name": "manager",
    "email": "manager@mailbox.com",
    "password": hash_password(BASE_PASSWORD),
}

NEW_TASK = {
    "name": "Today test task",
    "description": "Test description",
}

TASKS_LIST = [
    {
        "name": "Today test task 1",
        "description": "Test description 1",
    },
    {
        "name": "Today test task 2",
        "description": "Test description 2",
    },
    {
        "name": "Today test task 3",
        "description": "Test description 3",
    },
    {
        "name": "Today test task 4",
        "description": "Test description 4",
    },
    {
        "name": "Today test task 5",
        "description": "Test description 5",
    },
]
