"""
Seed the Knowledge Graph with Synthetic Evidence Atoms
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models import EvidenceAtom
from backend.engine import HELIXEngine
from backend.database import db
from backend.services.database_service import DatabaseService
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///helix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_service = DatabaseService()
db_service.init_app(app)

# Initialize engine with database service
engine = HELIXEngine(db_service=db_service)

# =============================================
# SYNTHETIC EVIDENCE ATOMS (Parkinson's Disease Focus)
# =============================================

SYNTHETIC_ATOMS = [
    # Core Parkinson's pathway
    {
        "subject": "Alpha-synuclein",
        "relationship": "aggregates in",
        "object": "Lewy bodies",
        "source": "synthetic:001",
        "confidence": 0.85,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Lewy bodies",
        "relationship": "are associated with",
        "object": "Parkinson's disease",
        "source": "synthetic:002",
        "confidence": 0.90,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Alpha-synuclein aggregation",
        "relationship": "activates",
        "object": "Microglial inflammation",
        "source": "synthetic:003",
        "confidence": 0.78,
        "study_type": "animal_study",
        "evidence_type": "experimental"
    },
    {
        "subject": "Microglial inflammation",
        "relationship": "contributes to",
        "object": "Neurodegeneration",
        "source": "synthetic:004",
        "confidence": 0.75,
        "study_type": "animal_study",
        "evidence_type": "experimental"
    },
    {
        "subject": "Anti-inflammatory pathway",
        "relationship": "reduces",
        "object": "Microglial activation",
        "source": "synthetic:005",
        "confidence": 0.70,
        "study_type": "animal_study",
        "evidence_type": "experimental"
    },
    {
        "subject": "Parkinson's disease",
        "relationship": "causes",
        "object": "motor symptoms",
        "source": "synthetic:006",
        "confidence": 0.88,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Dopamine depletion",
        "relationship": "leads to",
        "object": "motor symptoms",
        "source": "synthetic:007",
        "confidence": 0.87,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Alpha-synuclein",
        "relationship": "induces",
        "object": "oxidative stress",
        "source": "synthetic:008",
        "confidence": 0.72,
        "study_type": "cell_study",
        "evidence_type": "experimental"
    },
    {
        "subject": "Oxidative stress",
        "relationship": "causes",
        "object": "mitochondrial dysfunction",
        "source": "synthetic:009",
        "confidence": 0.68,
        "study_type": "cell_study",
        "evidence_type": "experimental"
    },
    {
        "subject": "Mitochondrial dysfunction",
        "relationship": "contributes to",
        "object": "Alpha-synuclein aggregation",
        "source": "synthetic:010",
        "confidence": 0.72,
        "study_type": "animal_study",
        "evidence_type": "experimental"
    },
    {
        "subject": "Neuroinflammation",
        "relationship": "exacerbates",
        "object": "Parkinson's disease",
        "source": "synthetic:011",
        "confidence": 0.80,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Microglia",
        "relationship": "release",
        "object": "inflammatory cytokines",
        "source": "synthetic:012",
        "confidence": 0.68,
        "study_type": "cell_study",
        "evidence_type": "experimental"
    },
    {
        "subject": "Inflammatory cytokines",
        "relationship": "contribute to",
        "object": "dopaminergic neuron death",
        "source": "synthetic:013",
        "confidence": 0.72,
        "study_type": "animal_study",
        "evidence_type": "experimental"
    },
    {
        "subject": "Dopaminergic neuron death",
        "relationship": "causes",
        "object": "motor symptoms",
        "source": "synthetic:014",
        "confidence": 0.85,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Parkinson's disease",
        "relationship": "is treated by",
        "object": "Levodopa",
        "source": "synthetic:015",
        "confidence": 0.92,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Levodopa",
        "relationship": "replaces",
        "object": "dopamine",
        "source": "synthetic:016",
        "confidence": 0.88,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Dopamine",
        "relationship": "improves",
        "object": "motor function",
        "source": "synthetic:017",
        "confidence": 0.85,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Amyloid-beta",
        "relationship": "accumulates in",
        "object": "Alzheimer's brain",
        "source": "synthetic:018",
        "confidence": 0.82,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Amyloid-beta",
        "relationship": "activates",
        "object": "Microglial inflammation",
        "source": "synthetic:019",
        "confidence": 0.76,
        "study_type": "animal_study",
        "evidence_type": "experimental"
    },
    {
        "subject": "Tau protein",
        "relationship": "hyperphosphorylates",
        "object": "neurofibrillary tangles",
        "source": "synthetic:020",
        "confidence": 0.80,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Neurofibrillary tangles",
        "relationship": "are associated with",
        "object": "Alzheimer's disease",
        "source": "synthetic:021",
        "confidence": 0.85,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Microglial inflammation",
        "relationship": "contributes to",
        "object": "Alzheimer's disease",
        "source": "synthetic:022",
        "confidence": 0.72,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Neuroinflammation",
        "relationship": "is a shared mechanism in",
        "object": "neurodegenerative diseases",
        "source": "synthetic:023",
        "confidence": 0.78,
        "study_type": "literature_review",
        "evidence_type": "systematic_review"
    },
    {
        "subject": "Microglial activation",
        "relationship": "is common in",
        "object": "Parkinson's disease",
        "source": "synthetic:024",
        "confidence": 0.75,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Microglial activation",
        "relationship": "is common in",
        "object": "Alzheimer's disease",
        "source": "synthetic:025",
        "confidence": 0.73,
        "study_type": "human_study",
        "evidence_type": "clinical_research"
    },
    {
        "subject": "Microglial activation",
        "relationship": "is common in",
        "object": "ALS",
        "source": "synthetic:026",
        "confidence": 0.70,
        "study_type": "animal_study",
        "evidence_type": "experimental"
    },
    {
        "subject": "Oxidative stress",
        "relationship": "is a common pathway in",
        "object": "neurodegenerative diseases",
        "source": "synthetic:027",
        "confidence": 0.76,
        "study_type": "literature_review",
        "evidence_type": "systematic_review"
    },
]

def seed_graph():
    """Seed the knowledge graph with synthetic evidence atoms."""
    with app.app_context():
        print("=" * 60)
        print("🧬 Seeding Knowledge Graph")
        print("=" * 60)
        
        # Clear existing data
        print("\n📊 Clearing existing data...")
        db_service.clear()
        print("✅ Data cleared.")
        
        # Add synthetic atoms
        print("\n📊 Adding synthetic evidence atoms...")
        for i, atom_data in enumerate(SYNTHETIC_ATOMS, 1):
            atom = EvidenceAtom(
                subject=atom_data["subject"],
                relationship=atom_data["relationship"],
                object=atom_data["object"],
                source=atom_data["source"],
                confidence=atom_data["confidence"],
                study_type=atom_data["study_type"],
                evidence_type=atom_data["evidence_type"],
            )
            engine.process(atom)
            print(f"   [{i}/{len(SYNTHETIC_ATOMS)}] Added: {atom.subject} → {atom.relationship} → {atom.object}")
        
        print(f"\n✅ Added {len(SYNTHETIC_ATOMS)} evidence atoms.")
        
        # Show stats
        print("\n📊 Database Statistics:")
        all_atoms = db_service.get_all_atoms()
        print(f"   Total evidence atoms: {len(all_atoms)}")
        stats = engine.get_stats()
        print(f"   Knowledge graph nodes: {stats['knowledge_graph']['nodes']}")
        print(f"   Knowledge graph edges: {stats['knowledge_graph']['edges']}")
        print("=" * 60)

if __name__ == "__main__":
    seed_graph()


