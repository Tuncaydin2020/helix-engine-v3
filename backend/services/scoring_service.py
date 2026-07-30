"""
HELIX Scoring Service
Clinical evidence evaluation with transparent reasoning.
"""

from typing import Tuple, List
from backend.models import EvidenceAtom

# =============================================
# CLINICAL WEIGHT TABLES
# These are the source of truth for all scoring.
# =============================================

STUDY_TYPE_WEIGHTS = {
    "meta_analysis": 0.50,
    "systematic_review": 0.45,
    "randomized_controlled_trial": 0.45,
    "cohort_study": 0.40,
    "human_study": 0.35,
    "clinical_research": 0.35,
    "observational_study": 0.30,
    "case_control_study": 0.30,
    "animal_study": 0.20,
    "cell_study": 0.15,
    "in_vitro": 0.15,
    "in_silico": 0.10,
    "literature_review": 0.15,
    "pubmed_import": 0.15,
    "unknown": 0.10,
}

EVIDENCE_TYPE_WEIGHTS = {
    "clinical_trial": 0.40,
    "clinical_research": 0.35,
    "experimental": 0.25,
    "observational": 0.30,
    "pubmed_import": 0.10,
    "other": 0.10,
    "unknown": 0.10,
}

CONFIDENCE_SCORES = {
    "very_high": 0.95,
    "high": 0.90,
    "moderate": 0.70,
    "exploratory": 0.50,
    "low": 0.40,
    "very_low": 0.20,
}

# =============================================
# SCORING SERVICE
# =============================================

class ScoringService:
    """Clinical evidence scoring service with transparent reasoning."""

    @staticmethod
    def score(atom: EvidenceAtom) -> Tuple[float, List[str]]:
        """
        Calculate a clinical evidence score and reasoning chain.

        The score is a weighted combination of:
        - Study Type (40%)
        - Evidence Type (20%)
        - Confidence (20%)
        - Sample Size Indicator (10%)
        - Replication Indicator (10%)
        """
        if not atom:
            return 0.0, []

        score = 0.0
        reason = []

        # 1. Study Type (40%)
        study_weight = STUDY_TYPE_WEIGHTS.get(atom.study_type, 0.10)
        study_contribution = study_weight * 0.40
        score += study_contribution
        reason.append(f"Study type ({atom.study_type}): +{study_contribution:.2f}")

        # 2. Evidence Type (20%)
        evidence_weight = EVIDENCE_TYPE_WEIGHTS.get(atom.evidence_type, 0.10)
        evidence_contribution = evidence_weight * 0.20
        score += evidence_contribution
        reason.append(f"Evidence type ({atom.evidence_type}): +{evidence_contribution:.2f}")

        # 3. Confidence (20%)
        if isinstance(atom.confidence, (int, float)):
            conf_weight = min(1.0, max(0.0, atom.confidence))
        else:
            conf_weight = CONFIDENCE_SCORES.get(atom.confidence, 0.40)
        conf_contribution = conf_weight * 0.20
        score += conf_contribution
        reason.append(f"Confidence ({atom.confidence}): +{conf_contribution:.2f}")

        # 4. Sample Size Indicator (10%)
        sample_weights = {
            "meta_analysis": 0.30,
            "systematic_review": 0.30,
            "randomized_controlled_trial": 0.25,
            "cohort_study": 0.25,
            "human_study": 0.20,
            "clinical_research": 0.20,
            "observational_study": 0.15,
            "case_control_study": 0.15,
            "animal_study": 0.10,
            "cell_study": 0.10,
            "in_vitro": 0.10,
            "in_silico": 0.05,
            "literature_review": 0.10,
            "pubmed_import": 0.10,
            "unknown": 0.05,
        }
        sample_weight = sample_weights.get(atom.study_type, 0.05)
        sample_contribution = sample_weight * 0.10
        score += sample_contribution
        reason.append(f"Sample size indicator: +{sample_contribution:.2f}")

        # 5. Replication Indicator (10%)
        replication_contribution = 0.10 * 0.10
        score += replication_contribution
        reason.append(f"Replication indicator: +{replication_contribution:.2f}")

        # Cap at 1.0
        final_score = min(1.0, max(0.0, score))
        return round(final_score, 3), reason

    @staticmethod
    def classify(score: float) -> str:
        """
        Classify evidence based on clinical significance thresholds.

        Thresholds are calibrated for biomedical research:
        - 0.70+: Strong clinical evidence
        - 0.50-0.69: Moderate clinical evidence
        - 0.30-0.49: Weak but meaningful evidence
        - < 0.30: Very weak evidence
        """
        if score >= 0.70:
            return "Strong Evidence"
        elif score >= 0.50:
            return "Moderate Evidence"
        elif score >= 0.30:
            return "Weak Evidence"
        else:
            return "Very Weak Evidence"

    @staticmethod
    def get_study_type_description(study_type: str) -> str:
        """Get a human-readable description of the study type."""
        descriptions = {
            "meta_analysis": "Highest quality - combines multiple studies",
            "systematic_review": "High quality - structured review of literature",
            "randomized_controlled_trial": "High quality - randomized intervention study",
            "cohort_study": "Good quality - large population observation",
            "human_study": "Direct human evidence",
            "clinical_research": "Direct clinical investigation",
            "observational_study": "Observed outcomes in populations",
            "case_control_study": "Compares cases vs controls",
            "animal_study": "Preclinical model evidence",
            "cell_study": "In vitro mechanistic evidence",
            "in_vitro": "Laboratory cell-based evidence",
            "in_silico": "Computational modeling evidence",
            "literature_review": "Expert summary of existing evidence",
            "pubmed_import": "Imported from PubMed database",
        }
        return descriptions.get(study_type, "Unknown study type")

