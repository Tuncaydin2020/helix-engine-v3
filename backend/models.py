"""
HELIX Data Models
"""

from typing import Dict, Any, Optional

class EvidenceAtom:
    def __init__(
        self,
        subject: str,
        relationship: str,
        object: str,
        source: str = "manual",
        confidence: float = 0.5,
        study_type: str = "unknown",
        evidence_type: str = "unknown",
    ):
        self.subject = subject
        self.relationship = relationship
        self.object = object
        self.source = source
        self.confidence = max(0.0, min(1.0, confidence))
        self.study_type = study_type
        self.evidence_type = evidence_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "relationship": self.relationship,
            "object": self.object,
            "source": self.source,
            "confidence": self.confidence,
            "study_type": self.study_type,
            "evidence_type": self.evidence_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceAtom":
        return cls(
            subject=data.get("subject"),
            relationship=data.get("relationship"),
            object=data.get("object"),
            source=data.get("source", "manual"),
            confidence=data.get("confidence", 0.5),
            study_type=data.get("study_type", "unknown"),
            evidence_type=data.get("evidence_type", "unknown"),
        )


class ReasoningResult:
    def __init__(
        self,
        atom: EvidenceAtom,
        score: float,
        classification: str,
        reasoning_chain: list,
        hypothesis: str,
    ):
        self.atom = atom
        self.score = score
        self.classification = classification
        self.reasoning_chain = reasoning_chain
        self.hypothesis = hypothesis

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence": self.atom.to_dict(),
            "analysis": {
                "score": self.score,
                "classification": self.classification,
                "reasoning": self.reasoning_chain,
                "hypothesis": self.hypothesis,
            },
        }
    