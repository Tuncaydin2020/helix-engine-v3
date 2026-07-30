"""
HELIX Knowledge Graph Service
Connects evidence atoms to discover pathways and relationships.
"""

from typing import List, Dict, Set

class KnowledgeGraphService:
    """Builds and queries a graph of scientific relationships."""

    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: List[Dict[str, str]] = []

    def add_atom(self, atom) -> None:
        """Add an evidence atom to the knowledge graph."""
        # Normalize to lowercase for case-insensitive matching
        subject = atom.subject.lower()
        object = atom.object.lower()
        relationship = atom.relationship.lower()
        
        print(f"🔍 Adding to graph: {subject} --{relationship}--> {object}")
        self.nodes.add(subject)
        self.nodes.add(object)
        self.edges.append({
            "subject": subject,
            "relationship": relationship,
            "object": object,
            "source": atom.source,
            "confidence": atom.confidence,
            "study_type": atom.study_type,
            "evidence_type": atom.evidence_type,
        })
        print(f"✅ Graph now has {len(self.nodes)} nodes and {len(self.edges)} edges")

    def load_from_db(self, db_service) -> None:
        """
        Load evidence atoms from the database into the knowledge graph.
        This is called by HELIXEngine on initialization.
        """
        print("📊 load_from_db() called")
        if not db_service:
            print("⚠️  No database service provided.")
            return
        
        print("📊 Fetching atoms from database...")
        atoms = db_service.get_all_atoms()
        print(f"📊 Retrieved {len(atoms)} atoms from database.")
        
        if not atoms:
            print("ℹ️  No atoms found in database.")
            return
        
        # Clear existing graph before loading
        self.nodes = set()
        self.edges = []
        
        for atom in atoms:
            self.add_atom(atom)
        
        print(f"📊 Graph loaded: {len(self.nodes)} nodes, {len(self.edges)} edges.")

    def get_connections(self, concept: str) -> List[Dict[str, str]]:
        """Get all relationships involving a concept."""
        concept = concept.lower()
        connections = []
        for edge in self.edges:
            if edge["subject"] == concept or edge["object"] == concept:
                connections.append(edge)
        return connections

    def find_pathways(self, start: str, end: str, max_depth: int = 5) -> List[List[str]]:
        """Find pathways between two concepts."""
        start = start.lower()
        end = end.lower()
        
        if start not in self.nodes:
            print(f"⚠️  Start node '{start}' not in graph")
            return []
        if end not in self.nodes:
            print(f"⚠️  End node '{end}' not in graph")
            return []

        pathways = []
        self._dfs(start, end, [start], pathways, max_depth)
        return pathways

    def _dfs(self, current: str, target: str, path: List[str], pathways: List[List[str]], max_depth: int):
        """Depth-first search for pathways."""
        if len(path) > max_depth:
            return
        if current == target and len(path) > 1:
            pathways.append(path.copy())
            return

        neighbors = []
        for edge in self.edges:
            if edge["subject"] == current and edge["object"] not in path:
                neighbors.append(edge["object"])
            elif edge["object"] == current and edge["subject"] not in path:
                neighbors.append(edge["subject"])

        for neighbor in neighbors:
            path.append(neighbor)
            self._dfs(neighbor, target, path, pathways, max_depth)
            path.pop()

    def get_statistics(self) -> Dict[str, int]:
        """Get graph statistics."""
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
        }

