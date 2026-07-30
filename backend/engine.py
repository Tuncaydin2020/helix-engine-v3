"""
HELIX Reasoning Engine
"""

from typing import List, Dict, Optional
from backend.models import EvidenceAtom, ReasoningResult
from backend.services.scoring_service import ScoringService
from backend.services.storage_service import StorageService
from backend.services.knowledge_graph_service import KnowledgeGraphService
from backend.services.pubmed_client import PubMedClient
from backend.services.reasoner_service import ReasonerService

class HELIXEngine:
    def __init__(self, db_service=None, app_context=None):
        self.scorer = ScoringService()
        self.storage = StorageService()
        self.graph = KnowledgeGraphService()
        self.pubmed = PubMedClient()
        self.db = db_service
        self.app_context = app_context
        self.reasoner = ReasonerService(self.graph)
        
        self.load_graph()
        print("🧬 HELIX Engine initialized.")

    def load_graph(self):
        """Load or reload the knowledge graph from the database."""
        print("📊 Loading graph from database...")
        if self.db and self.app_context:
            with self.app_context:
                atoms = self.db.get_all_atoms()
                print(f"📊 Found {len(atoms)} atoms in database.")
                self.graph.nodes = set()
                self.graph.edges = []
                for atom in atoms:
                    self.graph.add_atom(atom)
                print(f"📊 Graph loaded: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges.")
        else:
            print("⚠️  No database service or app context available. Graph is empty.")

    def process(self, atom: EvidenceAtom, user_id: Optional[int] = None) -> ReasoningResult:
        if self.db and self.app_context:
            with self.app_context:
                db_atom = self.db.save_atom(atom, user_id)
                atom_id = db_atom.id
        else:
            self.storage.save(atom)
            atom_id = None

        self.graph.add_atom(atom)

        score, reasoning_chain = self.scorer.score(atom)
        classification = self.scorer.classify(score)
        hypothesis = self._generate_hypothesis(atom, score)

        if self.db and self.app_context and atom_id:
            with self.app_context:
                self.db.save_report(atom_id, score, classification, reasoning_chain, hypothesis, user_id)

        return ReasoningResult(
            atom=atom,
            score=score,
            classification=classification,
            reasoning_chain=reasoning_chain,
            hypothesis=hypothesis,
        )

    def process_batch(self, atoms: List[EvidenceAtom]) -> List[ReasoningResult]:
        results = []
        for atom in atoms:
            results.append(self.process(atom))
        return results

    def _generate_hypothesis(self, atom: EvidenceAtom, score: float) -> str:
        if score >= 0.50:
            return f"Strong evidence suggests that {atom.subject} {atom.relationship} {atom.object}. Consider clinical translation."
        elif score >= 0.30:
            return f"Moderate evidence supports the association between {atom.subject} and {atom.object}. Further validation recommended."
        else:
            return f"Preliminary evidence suggests {atom.subject} may {atom.relationship} {atom.object}. Further investigation required."

    def get_stats(self) -> dict:
        stats = {
            "knowledge_graph": self.graph.get_statistics(),
        }
        if self.db:
            stats["database_atoms"] = self.db.count()
        return stats

    def find_pathways(self, start: str, end: str) -> List[List[str]]:
        return self.graph.find_pathways(start, end)

    def get_connections(self, concept: str) -> List[Dict[str, str]]:
        return self.graph.get_connections(concept)

    def import_pubmed_papers(self, query: str, max_papers: int = 100) -> List[EvidenceAtom]:
        print(f"📚 Searching PubMed for: {query}")
        pmids = self.pubmed.search(query, max_papers)
        print(f"📄 Found {len(pmids)} papers")
        
        imported_atoms = []
        for i, pmid in enumerate(pmids):
            print(f"   [{i+1}/{len(pmids)}] Processing PMID: {pmid}")
            paper = self.pubmed.fetch_details(pmid)
            if paper.get("title") == "No title":
                print(f"   ⚠️  Skipping - no title available")
                continue
            
            atom = EvidenceAtom(
                subject=query[:100],
                relationship="is associated with",
                object=paper["title"][:200],
                source=f"PMID: {pmid}",
                confidence=0.60,
                study_type="literature_review",
                evidence_type="pubmed_import",
                journal=paper.get("journal"),
                publication_date=paper.get("date"),
            )
            
            if self.db and self.app_context:
                with self.app_context:
                    self.db.save_atom(atom)
            else:
                self.storage.save(atom)
            self.graph.add_atom(atom)
            imported_atoms.append(atom)
            print(f"   ✅ Imported: {atom.subject} → {atom.relationship} → {atom.object[:50]}...")
        
        print(f"✅ Import complete! {len(imported_atoms)} papers imported.")
        return imported_atoms

    def reason(self) -> Dict:
        print("🧠 Running Scientific Reasoner...")
        self.load_graph()
        result = self.reasoner.reason()
        print(f"✅ Reasoning complete: {len(result['hypotheses'])} hypotheses generated.")
        return result

