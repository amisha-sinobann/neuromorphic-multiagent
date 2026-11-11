"""Thinker Agent – Reasons about the claims, structure, and potential risk areas."""

from .base import BaseAgent, AgentRole, AgentMessage, SharedMemory


class ThinkerAgent(BaseAgent):
    role = AgentRole.THINKER

    def run(self, memory: SharedMemory) -> AgentMessage:
        claims = memory.extracted_claims
        thought_parts = []

        thought_parts.append(
            f"I am reasoning over {len(claims)} extracted claims."
        )

        risk_areas = []
        high_risk_terms = [
            "always", "never", "guarantees", "orders of magnitude better in all cases",
            "replaces gpus", "fully biological", "zero power", "perfect accuracy",
            "on-chip learning on truenorth", "stdp solves all supervised learning"
        ]

        for i, claim in enumerate(claims):
            lower = claim.lower()
            risks = [t for t in high_risk_terms if t in lower]
            if risks:
                risk_areas.append({
                    "claim_index": i,
                    "claim": claim[:150],
                    "risk_terms": risks,
                    "reason": "Contains absolute or overstated language that often leads to hallucination or overclaiming."
                })

        # Also flag claims that mention hardware without context
        for i, claim in enumerate(claims):
            lower = claim.lower()
            if ("loihi" in lower or "truenorth" in lower or "spinnaker" in lower) and \
               ("learning" in lower or "accuracy" in lower or "energy" in lower):
                if not any(r["claim_index"] == i for r in risk_areas):
                    risk_areas.append({
                        "claim_index": i,
                        "claim": claim[:150],
                        "risk_terms": ["hardware claim"],
                        "reason": "Hardware performance or capability claims need grounding against known chip features."
                    })

        thought_parts.append(
            f"Identified {len(risk_areas)} higher-risk statements that need strong grounding from Recall."
        )
        if risk_areas:
            thought_parts.append(
                "Example risk: " + risk_areas[0]["reason"]
            )

        # Overall structure assessment
        if len(claims) < 3:
            thought_parts.append(
                "Document has few extractable claims — may be introductory or incomplete."
            )
        else:
            thought_parts.append(
                "Document contains multiple technical claims suitable for multi-agent verification."
            )

        thought = " | ".join(thought_parts)

        content = (
            f"Reasoning complete. Flagged {len(risk_areas)} statements that require careful "
            f"knowledge grounding to avoid hallucination."
        )

        msg = AgentMessage(
            role=self.role,
            content=content,
            thought=self._log_thought(thought),
            confidence=0.88,
            metadata={
                "risk_areas": risk_areas,
                "claim_count": len(claims),
            },
        )
        memory.add_trace(msg)
        return msg
