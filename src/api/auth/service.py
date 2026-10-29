from src.api.auth.schemas import LoginSchema, RequestUserSchema
from src.api.exceptions import (
    EmailAlreadyExistException,
    InvalidCredentialException,
    PasswordNotStrongException,
)
from src.api.units_of_work import AuthUnitOfWork
from src.config.security import (
    hash_password,
    is_password_strong_enough,
    verify_password,
)
from src.core.models.user import User


class AuthService:

    def __init__(self, uow: AuthUnitOfWork):
        self.uow = uow

    async def register(
        self,
        payload: RequestUserSchema,
    ) -> User:
        async with self.uow.atomic() as uow:
            await self._check_payload(payload)

            data = payload.model_dump(exclude_unset=True)
            data["password"] = hash_password(data["password"])

            new_user = await uow.user_repository.create(**data)
            return new_user

    async def login(self, payload: LoginSchema) -> User:
        async with self.uow.atomic() as uow:
            user = await uow.user_repository.get_by_email(payload.email)

            if not user or not verify_password(payload.password, user.password):
                raise InvalidCredentialException()

            return user

    async def update_provider(
        self, email: str, provider: str, provider_id: str
    ) -> User:
        async with self.uow.atomic() as uow:
            update_user = await uow.user_repository.get_by_email(email)
            user = await uow.user_repository.update(
                update_user, provider=provider, provider_id=provider_id
            )
            return user

    async def _check_payload(self, payload: RequestUserSchema) -> None:
        user_exist = await self.uow.user_repository.get_by_email(payload.email)
        if user_exist:
            raise EmailAlreadyExistException()

        if not is_password_strong_enough(payload.password):
            raise PasswordNotStrongException()
