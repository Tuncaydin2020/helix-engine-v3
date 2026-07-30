"""
Test the Reasoner Service directly with the graph.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.engine import HELIXEngine
from backend.services.database_service import DatabaseService
from backend.services.reasoner_service import ReasonerService
from flask import Flask

print("=" * 60)
print("🧬 Testing Reasoner Service")
print("=" * 60)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///helix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_service = DatabaseService()
db_service.init_app(app)

app_context = app.app_context()

engine = HELIXEngine(db_service=db_service, app_context=app_context)

print(f"Graph nodes: {len(engine.graph.nodes)}")
print(f"Graph edges: {len(engine.graph.edges)}")

reasoner = ReasonerService(engine.graph)

result = reasoner.reason()

print("\n📊 Reasoning Results:")
print(f"Converging Pathways: {len(result['converging_pathways'])}")
print(f"Contradictions: {len(result['contradictions'])}")
print(f"Knowledge Gaps: {len(result['knowledge_gaps'])}")
print(f"Hypotheses: {len(result['hypotheses'])}")

if result['hypotheses']:
    print("\n📊 Sample Hypotheses:")
    for h in result['hypotheses'][:3]:
        print(f"  • {h['hypothesis']}")
