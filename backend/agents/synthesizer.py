"""Synthesizer Agent – Produces the final human-readable report."""

from .base import BaseAgent, AgentRole, AgentMessage, SharedMemory


class SynthesizerAgent(BaseAgent):
    role = AgentRole.SYNTHESIZER

    def run(self, memory: SharedMemory) -> AgentMessage:
        issues = memory.potential_issues
        claims = memory.extracted_claims
        knowledge_count = len(memory.retrieved_knowledge)

        thought_parts = [
            "I am synthesizing the full multi-agent trace into a clear, actionable report "
            "that highlights where hallucination risk is highest."
        ]

        # Build structured report
        high = [i for i in issues if i["severity"] == "high"]
        medium = [i for i in issues if i["severity"] == "medium"]

        summary = {
            "overall_assessment": "",
            "claim_count": len(claims),
            "issues_found": len(issues),
            "high_severity": len(high),
            "medium_severity": len(medium),
            "knowledge_items_used": knowledge_count,
            "recommendations": [],
            "detailed_issues": issues,
            "agent_collaboration_note": (
                "This report was produced by a sequential multi-agent pipeline: "
                "Viewer → Thinker → Recall → Checker → Synthesizer. "
                "Each agent externalizes its reasoning (see / think / recall) to reduce silent hallucination."
            ),
        }

        if not issues:
            summary["overall_assessment"] = (
                "No strong hallucination or factual red flags were detected against the "
                "curated neuromorphic knowledge base. The document appears relatively careful, "
                "but this is not a guarantee of correctness — always verify critical claims with primary literature."
            )
            summary["recommendations"] = [
                "Have a domain expert review any quantitative performance numbers.",
                "Cite original papers for hardware capability claims (Loihi, TrueNorth, BrainScaleS, etc.).",
            ]
        else:
            summary["overall_assessment"] = (
                f"Found {len(issues)} potential issues ({len(high)} high severity). "
                "Several statements show patterns commonly associated with overclaiming "
                "or inaccurate understanding of neuromorphic hardware and algorithms."
            )
            summary["recommendations"] = [
                "Revise absolute language (always/never/guarantees) into conditional statements.",
                "Double-check hardware features against official Intel Loihi / IBM TrueNorth documentation.",
                "Distinguish clearly between rate coding and temporal coding when discussing SNNs.",
                "Avoid claiming that neuromorphic systems universally replace GPUs.",
                "Add citations for any energy-efficiency or accuracy numbers.",
            ]

        memory.final_report = summary

        thought_parts.append(
            f"Final report ready. Assessment: {summary['overall_assessment'][:100]}..."
        )
        thought = " | ".join(thought_parts)

        content = (
            f"Synthesis complete. Overall: {summary['overall_assessment']}"
        )

        msg = AgentMessage(
            role=self.role,
            content=content,
            thought=self._log_thought(thought),
            confidence=0.9,
            metadata={
                "report_keys": list(summary.keys()),
            },
        )
        memory.add_trace(msg)
        return msg
