"""Checker Agent – Detects potential hallucinations, factual errors, and overclaims."""

from .base import BaseAgent, AgentRole, AgentMessage, SharedMemory
from knowledge.neuromorphic_kb import get_all_mistakes
import re


class CheckerAgent(BaseAgent):
    role = AgentRole.CHECKER

    def run(self, memory: SharedMemory) -> AgentMessage:
        claims = memory.extracted_claims
        knowledge = memory.retrieved_knowledge
        known_mistakes = get_all_mistakes()
        issues = []

        thought_parts = [
            "I am cross-checking every extracted claim against recalled knowledge "
            "and the curated list of common neuromorphic myths to prevent hallucination."
        ]

        # 1. Direct match against known common mistakes
        for claim in claims:
            claim_lower = claim.lower()
            for mistake in known_mistakes:
                # Simple overlap check
                mistake_keywords = set(re.findall(r'\b\w{4,}\b', mistake.lower()))
                claim_keywords = set(re.findall(r'\b\w{4,}\b', claim_lower))
                overlap = mistake_keywords & claim_keywords
                if len(overlap) >= 3:
                    issues.append({
                        "type": "possible_common_mistake",
                        "severity": "high",
                        "claim": claim,
                        "matched_myth": mistake,
                        "explanation": (
                            "This claim shares significant language with a known overstatement "
                            "or misconception in neuromorphic research literature."
                        ),
                        "suggestion": "Verify against primary sources (Loihi papers, TrueNorth papers, recent SNN surveys)."
                    })

        # 2. Absolute language detector
        absolute_patterns = [
            r"\balways\b", r"\bnever\b", r"\bguarantees?\b", r"\bperfect\b",
            r"\bzero energy\b", r"\breplaces? (all )?gpus?\b", r"\bfully biological\b",
            r"\borders of magnitude (better|more efficient) in all\b"
        ]
        for claim in claims:
            for pat in absolute_patterns:
                if re.search(pat, claim, re.IGNORECASE):
                    issues.append({
                        "type": "overclaim_absolute_language",
                        "severity": "medium",
                        "claim": claim,
                        "matched_myth": None,
                        "explanation": (
                            "Absolute language is a frequent source of hallucinated or "
                            "over-generalized statements in AI research writing."
                        ),
                        "suggestion": "Qualify the statement with conditions, benchmarks, or 'under certain workloads'."
                    })
                    break

        # 3. Hardware capability sanity checks
        hardware_rules = [
            {
                "if_contains": ["truenorth", "learning"],
                "flag_if_not": ["limited", "not", "does not", "no on-chip"],
                "msg": "TrueNorth has very limited / no flexible on-chip learning compared to Loihi. Claims of rich on-chip learning on TrueNorth are often incorrect."
            },
            {
                "if_contains": ["snn", "always", "more accurate"],
                "flag_if_not": [],
                "msg": "SNNs do not always outperform ANNs on accuracy; they often trade accuracy for efficiency or temporal processing advantages."
            },
            {
                "if_contains": ["neuromorphic", "replace", "gpu"],
                "flag_if_not": ["sparse", "event-driven", "certain workloads"],
                "msg": "Neuromorphic hardware does not generally replace GPUs; it is complementary for sparse, low-power, event-driven tasks."
            },
        ]

        for claim in claims:
            claim_lower = claim.lower()
            for rule in hardware_rules:
                if all(term in claim_lower for term in rule["if_contains"]):
                    if not any(safe in claim_lower for safe in rule["flag_if_not"]):
                        issues.append({
                            "type": "hardware_capability_risk",
                            "severity": "high",
                            "claim": claim,
                            "matched_myth": None,
                            "explanation": rule["msg"],
                            "suggestion": "Cross-check against the original chip papers and recent surveys."
                        })

        # Deduplicate roughly
        unique_issues = []
        seen = set()
        for iss in issues:
            key = (iss["type"], iss["claim"][:80])
            if key not in seen:
                seen.add(key)
                unique_issues.append(iss)

        memory.potential_issues = unique_issues

        thought_parts.append(
            f"Found {len(unique_issues)} potential issues (hallucination risks, overclaims, or factual red flags)."
        )
        if unique_issues:
            thought_parts.append(
                "Highest severity example: " + unique_issues[0]["explanation"][:120]
            )
        else:
            thought_parts.append(
                "No strong red flags detected against the knowledge base. Still recommend human expert review."
            )

        thought = " | ".join(thought_parts)

        content = (
            f"Checking complete. Identified {len(unique_issues)} potential mistakes or "
            f"hallucination risks. Detailed findings passed to the Synthesizer."
        )

        msg = AgentMessage(
            role=self.role,
            content=content,
            thought=self._log_thought(thought),
            confidence=0.85,
            metadata={
                "issue_count": len(unique_issues),
                "high_severity": sum(1 for i in unique_issues if i["severity"] == "high"),
            },
        )
        memory.add_trace(msg)
        return msg
