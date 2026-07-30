"""
HELIX Storage Service
"""

import json
import os
from typing import List, Optional
from datetime import datetime
from backend.models import EvidenceAtom

class StorageService:
    def __init__(self, data_dir: str = "data/atoms"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def save(self, atom: EvidenceAtom) -> Optional[str]:
        existing = self.get_by_source(atom.source)
        if existing:
            print(f"ℹ️  Duplicate: '{atom.source}' already exists.")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"atom_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, "w") as f:
            json.dump(atom.to_dict(), f, indent=2)

        return filepath

    def get_by_source(self, source: str) -> Optional[EvidenceAtom]:
        if not source:
            return None
        for atom in self.load_all():
            if atom.source == source:
                return atom
        return None

    def load_all(self) -> List[EvidenceAtom]:
        atoms = []
        if not os.path.exists(self.data_dir):
            return atoms

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.data_dir, filename), "r") as f:
                    data = json.load(f)
                    atoms.append(EvidenceAtom.from_dict(data))
        return atoms

    def count(self) -> int:
        return len(self.load_all())
    