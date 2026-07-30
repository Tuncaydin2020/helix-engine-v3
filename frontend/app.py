"""
HELIX Web Dashboard
"""

import sys
import os
import csv
from io import StringIO, BytesIO
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from backend.models import EvidenceAtom
from backend.engine import HELIXEngine
from backend.database import db, UserModel
from backend.services.database_service import DatabaseService
from backend.services.auth_service import AuthService

# PDF Report Libraries
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

app = Flask(__name__)

# Configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///helix.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(UserModel, int(user_id))

# Initialize database
db_service = DatabaseService()
db_service.init_app(app)

# Initialize engine with database service
engine = HELIXEngine(db_service=db_service)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    subject = request.form.get("subject", "").strip()
    relationship = request.form.get("relationship", "").strip()
    object = request.form.get("object", "").strip()
    source = request.form.get("source", "manual").strip()

    try:
        confidence = float(request.form.get("confidence", 0.5))
    except ValueError:
        confidence = 0.5

    study_type = request.form.get("study_type", "unknown").strip()
    evidence_type = request.form.get("evidence_type", "unknown").strip()

    atom = EvidenceAtom(
        subject=subject,
        relationship=relationship,
        object=object,
        source=source,
        confidence=confidence,
        study_type=study_type,
        evidence_type=evidence_type,
    )

    result = engine.process(atom, user_id=current_user.id)
    return render_template("results.html", result=result)

@app.route("/connections/<concept>")
@login_required
def connections(concept):
    """Show connections for a concept."""
    connections = engine.get_connections(concept)
    return render_template("connections.html", concept=concept, connections=connections)

@app.route("/pathways")
@login_required
def pathways_form():
    """Form to find pathways."""
    return render_template("pathways.html")

@app.route("/pathways/result")
@login_required
def pathways_result():
    """Find and display pathways between two concepts."""
    start = request.args.get("start", "").strip()
    end = request.args.get("end", "").strip()
    
    if not start or not end:
        return redirect(url_for("pathways_form"))
    
    pathways = engine.find_pathways(start, end)
    return render_template("pathways_result.html", start=start, end=end, pathways=pathways)

@app.route("/report/<source>")
@login_required
def generate_report(source):
    """
    Generate a PDF report for a specific evidence atom.
    The atom is retrieved by its 'source' identifier.
    """
    atom = engine.storage.get_by_source(source)
    if not atom:
        return "Atom not found", 404

    # Process the atom to get the reasoning result
    result = engine.process(atom, user_id=current_user.id)

    # Create the PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a5f'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    # Content
    story = []

    # 1. Title
    story.append(Paragraph("🧬 HELIX Scientific Report", title_style))
    story.append(Spacer(1, 0.25*inch))

    # 2. Evidence
    story.append(Paragraph("📋 Evidence", styles['Heading2']))
    story.append(Paragraph(f"<b>Subject:</b> {atom.subject}", styles['Normal']))
    story.append(Paragraph(f"<b>Relationship:</b> {atom.relationship}", styles['Normal']))
    story.append(Paragraph(f"<b>Object:</b> {atom.object}", styles['Normal']))
    story.append(Paragraph(f"<b>Source:</b> {atom.source}", styles['Normal']))
    story.append(Paragraph(f"<b>Confidence:</b> {atom.confidence}", styles['Normal']))
    story.append(Spacer(1, 0.25*inch))

    # 3. Analysis
    story.append(Paragraph("📊 Analysis", styles['Heading2']))
    story.append(Paragraph(f"<b>Score:</b> {result.score:.3f}", styles['Normal']))
    story.append(Paragraph(f"<b>Classification:</b> {result.classification}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))

    # 4. Reasoning Chain
    story.append(Paragraph("🔍 Reasoning", styles['Heading2']))
    for line in result.reasoning_chain:
        story.append(Paragraph(f"• {line}", styles['Normal']))
    story.append(Spacer(1, 0.25*inch))

    # 5. Hypothesis
    story.append(Paragraph("🧠 Hypothesis", styles['Heading2']))
    story.append(Paragraph(result.hypothesis, styles['Normal']))
    story.append(Spacer(1, 0.25*inch))

    # 6. Footer
    story.append(Paragraph(f"<i>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>", styles['Normal']))

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name=f"HELIX_Report_{atom.source}.pdf",
                     mimetype='application/pdf')

@app.route("/pubmed")
@login_required
def pubmed_search_page():
    """Show the PubMed search page."""
    return render_template("pubmed.html")

@app.route("/pubmed/import", methods=["POST"])
@login_required
def pubmed_import():
    """Import papers from PubMed and display results."""
    query = request.form.get("query", "").strip()
    if not query:
        return redirect("/pubmed")
    
    max_papers = 5
    papers = engine.import_pubmed_papers(query, max_papers)
    
    return render_template("pubmed_results.html", query=query, papers=papers)

@app.route("/batch")
@login_required
def batch_page():
    """Show the batch analysis page."""
    return render_template("batch.html")

@app.route("/batch/template")
@login_required
def batch_template():
    """Download a CSV template for batch analysis."""
    template = """subject,relationship,object,confidence,study_type,evidence_type,source
Alpha-synuclein,aggregates in,Lewy bodies,0.85,human_study,clinical_research,PMID:123
Dopamine,causes,motor symptoms,0.90,human_study,clinical_research,PMID:456
Amyloid-beta,accumulates in,Alzheimer's brain,0.70,animal_study,experimental,PMID:789
Parkinson's disease,is associated with,progressive motor decline,0.80,observational_study,observational,PMID:101112"""
    
    return send_file(
        StringIO(template),
        as_attachment=True,
        download_name="helix_batch_template.csv",
        mimetype="text/csv"
    )

@app.route("/batch/process", methods=["POST"])
@login_required
def batch_process():
    """Process a batch of evidence atoms."""
    results = []
    
    # Check if CSV file was uploaded
    if 'csv_file' in request.files and request.files['csv_file'].filename:
        csv_file = request.files['csv_file']
        csv_data = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_data))
        
        for row in csv_reader:
            try:
                atom = EvidenceAtom(
                    subject=row.get('subject', '').strip(),
                    relationship=row.get('relationship', '').strip(),
                    object=row.get('object', '').strip(),
                    source=row.get('source', 'batch').strip(),
                    confidence=float(row.get('confidence', 0.5)),
                    study_type=row.get('study_type', 'unknown').strip(),
                    evidence_type=row.get('evidence_type', 'unknown').strip(),
                )
                result = engine.process(atom, user_id=current_user.id)
                results.append(result)
            except Exception as e:
                print(f"⚠️  Error processing row: {e}")
                continue
    else:
        # Process text input
        text_data = request.form.get('batch_data', '').strip()
        if text_data:
            lines = text_data.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    parts = line.split(',')
                    if len(parts) >= 3:
                        try:
                            atom = EvidenceAtom(
                                subject=parts[0].strip(),
                                relationship=parts[1].strip(),
                                object=parts[2].strip(),
                                source=parts[6].strip() if len(parts) > 6 else 'batch',
                                confidence=float(parts[3].strip()) if len(parts) > 3 else 0.5,
                                study_type=parts[4].strip() if len(parts) > 4 else 'unknown',
                                evidence_type=parts[5].strip() if len(parts) > 5 else 'unknown',
                            )
                            result = engine.process(atom, user_id=current_user.id)
                            results.append(result)
                        except Exception as e:
                            print(f"⚠️  Error processing line: {e}")
                            continue
    
    return render_template("batch_results.html", results=results)

@app.route("/db/stats")
@login_required
def db_stats():
    """Show database statistics."""
    from backend.database import EvidenceAtomModel, ReportModel, UserModel
    
    atom_count = EvidenceAtomModel.query.filter_by(user_id=current_user.id).count()
    report_count = ReportModel.query.filter_by(user_id=current_user.id).count()
    user_count = UserModel.query.count()
    
    return render_template("db_stats.html", 
                         atom_count=atom_count, 
                         report_count=report_count, 
                         user_count=user_count)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        user, error = AuthService.login_user(username, password)
        if user:
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error=error)
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register page."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        
        user, error = AuthService.register_user(username, email, password)
        if user:
            login_user(user)
            return redirect(url_for("index"))
        else:
            return render_template("register.html", error=error)
    
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    """Logout page."""
    AuthService.logout_user()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)

