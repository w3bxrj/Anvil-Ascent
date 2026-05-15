from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum

class IssueType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    OTHER = "other"

class Priority(str, Enum):
    CRITICAL = "critical"      # P0 - crash, data loss, security
    HIGH = "high"              # P1 - major functionality broken
    MEDIUM = "medium"          # P2 - minor bug, nice-to-have feature
    LOW = "low"                # P3 - cosmetic, docs typo

class IssuePayload(BaseModel):
    """GitHub Issue Webhook Payload"""
    action: str
    issue: dict
    repository: dict
    sender: dict
    
    model_config = ConfigDict(extra="allow")

class ParsedIssue(BaseModel):
    """Cleaned & structured issue data"""
    id: int
    number: int
    title: str
    body: Optional[str] = ""
    state: str
    labels: List[str] = []
    author: str
    created_at: datetime
    updated_at: datetime
    url: str
    repo_name: str
    repo_full_name: str
    
    # Derived fields
    issue_type: IssueType = IssueType.OTHER
    priority: Priority = Priority.MEDIUM
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    extracted_keywords: List[str] = []
    
    def to_processing_context(self) -> dict:
        """Convert to dict for downstream agents"""
        return {
            "issue_id": self.id,
            "number": self.number,
            "title": self.title,
            "body": self.body,
            "type": self.issue_type.value,
            "priority": self.priority.value,
            "labels": self.labels,
            "keywords": self.extracted_keywords,
            "repo": self.repo_full_name,
            "url": self.url
        }