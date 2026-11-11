"""Base classes and shared state for the multi-agent system."""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
import uuid
from datetime import datetime


class AgentRole(str, Enum):
    VIEWER = "viewer"          # Sees / extracts content
    THINKER = "thinker"        # Reasons about structure & claims
    RECALL = "recall"          # Retrieves grounded knowledge
    CHECKER = "checker"        # Detects hallucinations & mistakes
    SYNTHESIZER = "synthesizer"  # Produces final report


@dataclass
class AgentMessage:
    role: AgentRole
    content: str
    thought: str = ""          # Internal reasoning (see / think / recall)
    confidence: float = 0.8
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict = field(default_factory=dict)


@dataclass
class SharedMemory:
    """Shared working memory across agents to reduce hallucination via grounding."""
    document_id: str
    original_text: str
    extracted_claims: list[str] = field(default_factory=list)
    retrieved_knowledge: list[dict] = field(default_factory=list)
    potential_issues: list[dict] = field(default_factory=list)
    agent_trace: list[AgentMessage] = field(default_factory=list)
    final_report: Optional[dict] = None

    def add_trace(self, msg: AgentMessage):
        self.agent_trace.append(msg)

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "extracted_claims": self.extracted_claims,
            "retrieved_knowledge": self.retrieved_knowledge,
            "potential_issues": self.potential_issues,
            "agent_trace": [
                {
                    "role": m.role.value,
                    "content": m.content,
                    "thought": m.thought,
                    "confidence": m.confidence,
                    "timestamp": m.timestamp,
                    "metadata": m.metadata,
                }
                for m in self.agent_trace
            ],
            "final_report": self.final_report,
        }


class BaseAgent:
    role: AgentRole

    def __init__(self, name: str = None):
        self.name = name or self.role.value
        self.id = str(uuid.uuid4())[:8]

    def run(self, memory: SharedMemory) -> AgentMessage:
        raise NotImplementedError

    def _log_thought(self, thought: str) -> str:
        """Force the agent to externalize its reasoning (anti-hallucination practice)."""
        return f"[{self.role.value.upper()}] {thought}"
