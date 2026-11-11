"""Viewer Agent – Sees the document, extracts structure and candidate claims."""

from .base import BaseAgent, AgentRole, AgentMessage, SharedMemory
import re


class ViewerAgent(BaseAgent):
    role = AgentRole.VIEWER

    def run(self, memory: SharedMemory) -> AgentMessage:
        text = memory.original_text
        thought_parts = []

        # See: basic stats
        word_count = len(text.split())
        char_count = len(text)
        thought_parts.append(
            f"I see a document of ~{word_count} words / {char_count} characters."
        )

        # Extract sentences that look like claims (contain strong verbs / numbers / proper nouns)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        candidate_claims = []
        claim_keywords = [
            "is", "are", "can", "enables", "achieves", "uses", "implements",
            "demonstrates", "shows", "provides", "supports", "based on",
            "loihi", "truenorth", "spinnaker", "stdp", "snn", "memristor",
            "energy", "power", "accuracy", "spike", "neuron"
        ]

        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) < 20:
                continue
            lower = s_clean.lower()
            # More permissive: keyword match OR reasonably long sentence
            has_keyword = any(k in lower for k in claim_keywords)
            long_enough = len(s_clean.split()) >= 6
            if has_keyword or (long_enough and len(s_clean) > 50):
                candidate_claims.append(s_clean)

        # Limit to most relevant
        candidate_claims = candidate_claims[:12]
        memory.extracted_claims = candidate_claims

        thought_parts.append(
            f"I extracted {len(candidate_claims)} candidate scientific claims for further checking."
        )
        if candidate_claims:
            thought_parts.append("First claim preview: " + candidate_claims[0][:120] + "...")

        thought = " | ".join(thought_parts)

        content = (
            f"Document viewed successfully. "
            f"Extracted {len(candidate_claims)} candidate claims for the Thinker and Checker agents."
        )

        msg = AgentMessage(
            role=self.role,
            content=content,
            thought=self._log_thought(thought),
            confidence=0.95,
            metadata={
                "word_count": word_count,
                "claim_count": len(candidate_claims),
                "claims_preview": candidate_claims[:3],
            },
        )
        memory.add_trace(msg)
        return msg
