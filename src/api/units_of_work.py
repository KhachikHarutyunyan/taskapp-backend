from src.api.auth.repository import UserRepository
from src.api.task.repository import TaskRepository
from src.core.base_uow import BaseUnitOfWork


class AuthUnitOfWork(BaseUnitOfWork):

    def __init__(self, session):
        super().__init__(session)
        self.user_repository = UserRepository(session)


class TaskUnitOfWork(BaseUnitOfWork):

    def __init__(self, session):
        super().__init__(session)
        self.user_repository = UserRepository(session)
        self.task_repository = TaskRepository(session)
