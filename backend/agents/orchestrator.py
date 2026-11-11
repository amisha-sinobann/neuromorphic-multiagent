"""Orchestrator – runs the multi-agent pipeline in sequence with shared memory."""

from .base import SharedMemory
from .viewer import ViewerAgent
from .thinker import ThinkerAgent
from .recall import RecallAgent
from .checker import CheckerAgent
from .synthesizer import SynthesizerAgent
import uuid


class MultiAgentOrchestrator:
    def __init__(self):
        self.agents = [
            ViewerAgent(),
            ThinkerAgent(),
            RecallAgent(),
            CheckerAgent(),
            SynthesizerAgent(),
        ]

    def process_document(self, text: str) -> dict:
        """Run the full see → think → recall → check → synthesize pipeline."""
        if not text or len(text.strip()) < 50:
            return {
                "error": "Document too short or empty. Please provide a meaningful research text.",
                "document_id": None,
            }

        memory = SharedMemory(
            document_id=str(uuid.uuid4()),
            original_text=text.strip(),
        )

        for agent in self.agents:
            agent.run(memory)

        return memory.to_dict()
