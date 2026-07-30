"""
HELIX Reasoning Engine
"""

from typing import List, Dict
from backend.models import EvidenceAtom, ReasoningResult
from backend.services.scoring_service import ScoringService
from backend.services.storage_service import StorageService
from backend.services.knowledge_graph_service import KnowledgeGraphService

class HELIXEngine:
    def __init__(self):
        self.scorer = ScoringService()
        self.storage = StorageService()
        self.graph = KnowledgeGraphService()
        print("🧬 HELIX Engine initialized with Knowledge Graph.")

    def process(self, atom: EvidenceAtom) -> ReasoningResult:
        """Process a single evidence atom through the full pipeline."""
        # 1. Store the atom
        self.storage.save(atom)

        # 2. Add to the knowledge graph
        self.graph.add_atom(atom)

        # 3. Score the atom
        score, reasoning_chain = self.scorer.score(atom)
        classification = self.scorer.classify(score)

        # 4. Generate a clinically specific hypothesis
        hypothesis = self._generate_hypothesis(atom, score)

        return ReasoningResult(
            atom=atom,
            score=score,
            classification=classification,
            reasoning_chain=reasoning_chain,
            hypothesis=hypothesis,
        )

    def _generate_hypothesis(self, atom: EvidenceAtom, score: float) -> str:
        """Generate a clinically specific hypothesis."""
        if score >= 0.50:
            return f"Strong evidence suggests that {atom.subject} {atom.relationship} {atom.object}. Consider clinical translation."
        elif score >= 0.30:
            return f"Moderate evidence supports the association between {atom.subject} and {atom.object}. Further validation recommended."
        else:
            return f"Preliminary evidence suggests {atom.subject} may {atom.relationship} {atom.object}. Further investigation required."

    def get_stats(self) -> dict:
        """Get system statistics."""
        return {
            "total_atoms": self.storage.count(),
            "knowledge_graph": self.graph.get_statistics(),
        }

    def find_pathways(self, start: str, end: str) -> List[List[str]]:
        """Find pathways between two concepts."""
        return self.graph.find_pathways(start, end)

    def get_connections(self, concept: str) -> List[Dict[str, str]]:
        """Get all connections for a concept."""
        return self.graph.get_connections(concept)


