from pydantic import BaseModel


class IssueInfo(BaseModel):
    task: str
    guidelines: str
    requirements: str
