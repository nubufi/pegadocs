from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class TaskCreationResponse(BaseModel):
    task_id: str


class TaskResult(BaseModel):
    """Returned when task completed successfully."""

    result: Optional[Dict[str, Any]] = None


class TaskError(BaseModel):
    """Returned when task failed."""

    error_type: str
    error_message: str


class TaskStatusResponse(BaseModel):
    """
    General-purpose task monitor response.
    Mirrors TaskService.get_result() unified structure.
    """

    task_id: str = Field(..., description="Unique task identifier")
    status: Literal["PROCESSING", "DONE", "ERROR", "UNKNOWN"]
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    created_at: Optional[int] = None  # epoch seconds
    updated_at: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[TaskError] = None
