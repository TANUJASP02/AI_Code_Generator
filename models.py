from pydantic import BaseModel


class CodeGenerationRequest(BaseModel):
    instruction: str
    repository_files: dict[str, str]


class FileSelectionResult(BaseModel):
    file_path: str
    explanation: str


class CodeGenerationResult(BaseModel):
    code: str
    explanation: str = ""


class EvaluationResult(BaseModel):
    score: int
    status: str
    feedback: str


class InstructionResult(BaseModel):
    instruction: str