"""
HELIX Database Layer
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from typing import Optional
import json

db = SQLAlchemy()

class UserModel(db.Model, UserMixin):
    """Database model for users."""
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    atoms = db.relationship("EvidenceAtomModel", backref="user", lazy=True)
    reports = db.relationship("ReportModel", backref="user", lazy=True)
    
    def get_id(self):
        return str(self.id)

class EvidenceAtomModel(db.Model):
    """Database model for evidence atoms."""
    __tablename__ = "evidence_atoms"
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(500), nullable=False)
    relationship = db.Column(db.String(500), nullable=False)
    object = db.Column(db.String(500), nullable=False)
    source = db.Column(db.String(200), nullable=False)
    confidence = db.Column(db.Float, nullable=False, default=0.5)
    study_type = db.Column(db.String(100), default="unknown")
    evidence_type = db.Column(db.String(100), default="unknown")
    journal = db.Column(db.String(200))
    publication_date = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "relationship": self.relationship,
            "object": self.object,
            "source": self.source,
            "confidence": self.confidence,
            "study_type": self.study_type,
            "evidence_type": self.evidence_type,
            "journal": self.journal,
            "publication_date": self.publication_date,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def to_evidence_atom(self):
        """Convert database model to EvidenceAtom object."""
        from backend.models import EvidenceAtom
        return EvidenceAtom(
            subject=self.subject,
            relationship=self.relationship,
            object=self.object,
            source=self.source,
            confidence=self.confidence,
            study_type=self.study_type,
            evidence_type=self.evidence_type,
            journal=self.journal,
            publication_date=self.publication_date,
        )


class ReportModel(db.Model):
    """Database model for reports."""
    __tablename__ = "reports"
    
    id = db.Column(db.Integer, primary_key=True)
    atom_id = db.Column(db.Integer, db.ForeignKey("evidence_atoms.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)
    classification = db.Column(db.String(100), nullable=False)
    reasoning_chain = db.Column(db.Text, nullable=False)  # JSON string
    hypothesis = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)


