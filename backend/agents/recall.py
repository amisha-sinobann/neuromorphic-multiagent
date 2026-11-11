"""Recall Agent – Retrieves grounded knowledge to combat hallucination."""

from .base import BaseAgent, AgentRole, AgentMessage, SharedMemory
from knowledge.neuromorphic_kb import search_knowledge, get_all_mistakes


class RecallAgent(BaseAgent):
    role = AgentRole.RECALL

    def run(self, memory: SharedMemory) -> AgentMessage:
        claims = memory.extracted_claims
        thought_parts = []
        all_retrieved = []

        thought_parts.append(
            "I am recalling grounded knowledge from the neuromorphic knowledge base "
            "to provide factual anchors for the Checker."
        )

        # Search for each claim (or top ones)
        for claim in claims[:8]:
            results = search_knowledge(claim, top_k=3)
            for r in results:
                if r not in all_retrieved:
                    all_retrieved.append(r)

        # Also always pull the common mistakes list for the checker
        mistakes = get_all_mistakes()
        thought_parts.append(
            f"Retrieved {len(all_retrieved)} knowledge snippets + {len(mistakes)} known common mistakes/myths."
        )

        if all_retrieved:
            thought_parts.append(
                "Sample grounding: " + all_retrieved[0]["content"][:100] + "..."
            )

        memory.retrieved_knowledge = all_retrieved

        thought = " | ".join(thought_parts)

        content = (
            f"Recall complete. Provided {len(all_retrieved)} grounded knowledge items "
            f"and the curated list of common neuromorphic misconceptions for the Checker agent."
        )

        msg = AgentMessage(
            role=self.role,
            content=content,
            thought=self._log_thought(thought),
            confidence=0.92,
            metadata={
                "retrieved_count": len(all_retrieved),
                "knowledge_preview": [r["source"] for r in all_retrieved[:5]],
                "common_mistakes_count": len(mistakes),
            },
        )
        memory.add_trace(msg)
        return msg
