from typing import Any, Dict

from src.api.task.schemas import (
    TaskFullResponseSchema,
    TaskResponseSchema,
)
from src.core.models import Task


class TasksDTOFactory:
    """DTO Factory for object Task"""

    @staticmethod
    def _extract_base_dto(payload: Task) -> Dict[str, Any]:
        """Extract payload to Base DTO for response"""
        return {
            "id": str(payload.id),
            "author_id": str(payload.author_id),
            "name": payload.name,
            "description": payload.description,
            "status": payload.status,
            "created_at": payload.created_at,
            "updated_at": payload.updated_at,
        }


    @classmethod
    def create_base_dto(cls, payload: Task) -> TaskResponseSchema:
        """Base DTO operation"""
        base_dto = cls._extract_base_dto(payload)
        return TaskResponseSchema(**base_dto)

    @classmethod
    def create_dto_for_list(cls, payload: Task) -> Dict[str, Any]:
        """Base DTO operation for list"""
        base_dto = cls._extract_base_dto(payload)
        return base_dto

    @classmethod
    def create_full_dto(cls, payload: Task) -> TaskFullResponseSchema:
        """Full DTO operation with relationship"""
        base_dto = cls._extract_base_dto(payload)
        extra_data = {}

        # Add relationship data if its exist
        if hasattr(payload, "executors") and payload.executors:
            executors_data = cls._extract_executors_data(payload.executors)
            extra_data["executors"] = executors_data if executors_data else None

        return TaskFullResponseSchema(**{**base_dto, **extra_data})
