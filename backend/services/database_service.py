"""
HELIX Database Service
"""

import json
from typing import List, Optional
from backend.database import db, EvidenceAtomModel, ReportModel, UserModel
from backend.models import EvidenceAtom

class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        self._initialized = False
    
    def init_app(self, app):
        """Initialize the database with the Flask app."""
        db.init_app(app)
        with app.app_context():
            db.create_all()
        self._initialized = True
    
    def save_atom(self, atom: EvidenceAtom, user_id: Optional[int] = None) -> EvidenceAtomModel:
        """Save an evidence atom to the database."""
        # Check if atom with same source already exists
        existing = EvidenceAtomModel.query.filter_by(source=atom.source).first()
        if existing:
            # Update existing atom
            existing.subject = atom.subject
            existing.relationship = atom.relationship
            existing.object = atom.object
            existing.confidence = atom.confidence
            existing.study_type = atom.study_type
            existing.evidence_type = atom.evidence_type
            existing.journal = atom.journal
            existing.publication_date = atom.publication_date
            if user_id:
                existing.user_id = user_id
            db.session.commit()
            return existing
        
        # Create new atom
        model = EvidenceAtomModel(
            subject=atom.subject,
            relationship=atom.relationship,
            object=atom.object,
            source=atom.source,
            confidence=atom.confidence,
            study_type=atom.study_type,
            evidence_type=atom.evidence_type,
            journal=atom.journal,
            publication_date=atom.publication_date,
            user_id=user_id,
        )
        db.session.add(model)
        db.session.commit()
        return model
    
    def get_atom_by_source(self, source: str, user_id: Optional[int] = None) -> Optional[EvidenceAtomModel]:
        """Get an atom by its source."""
        query = EvidenceAtomModel.query.filter_by(source=source)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        return query.first()
    
    def get_all_atoms(self, user_id: Optional[int] = None) -> List[EvidenceAtom]:
        """Get all atoms as EvidenceAtom objects."""
        query = EvidenceAtomModel.query
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        
        models = query.all()
        return [model.to_evidence_atom() for model in models]
    
    def get_all_atom_models(self, user_id: Optional[int] = None) -> List[EvidenceAtomModel]:
        """Get all atom models."""
        query = EvidenceAtomModel.query
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        return query.all()
    
    def save_report(self, atom_id: int, score: float, classification: str, 
                    reasoning_chain: list, hypothesis: str, user_id: Optional[int] = None):
        """Save a report to the database."""
        report = ReportModel(
            atom_id=atom_id,
            score=score,
            classification=classification,
            reasoning_chain=json.dumps(reasoning_chain),
            hypothesis=hypothesis,
            user_id=user_id,
        )
        db.session.add(report)
        db.session.commit()
        return report
    
    def count(self, user_id: Optional[int] = None) -> int:
        """Get total number of atoms."""
        query = EvidenceAtomModel.query
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        return query.count()
    
    def clear(self):
        """Clear all data (for testing)."""
        db.session.query(EvidenceAtomModel).delete()
        db.session.query(ReportModel).delete()
        db.session.query(UserModel).delete()
        db.session.commit()


