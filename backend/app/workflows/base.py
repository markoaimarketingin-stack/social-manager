from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

WorkflowInputT = TypeVar("WorkflowInputT", bound=BaseModel)
WorkflowOutputT = TypeVar("WorkflowOutputT", bound=BaseModel)


class Workflow(ABC, Generic[WorkflowInputT, WorkflowOutputT]):
    @abstractmethod
    async def run(self, workflow_input: WorkflowInputT) -> WorkflowOutputT:
        raise NotImplementedError
