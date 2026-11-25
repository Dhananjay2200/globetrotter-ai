import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "GlobeTrotter AI — Backend Architecture & File Guide")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 750, 558, 750)
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — GLOBETROTTER AI")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()


def build_pdf(filename="GlobeTrotter_AI_Backend_Documentation.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom color palette
    c_primary = colors.HexColor("#0F172A")    # Slate 900
    c_teal = colors.HexColor("#0D9488")       # Teal 600
    c_amber = colors.HexColor("#D97706")      # Amber 600
    c_text = colors.HexColor("#334155")       # Slate 700
    c_light = colors.HexColor("#F8FAFC")      # Slate 50
    c_border = colors.HexColor("#E2E8F0")     # Slate 200

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_teal,
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_teal,
        spaceBefore=10,
        spaceAfter=3,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=c_text,
        spaceAfter=6,
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )

    story = []

    # Title & Metadata Card
    story.append(Paragraph("GlobeTrotter AI", title_style))
    story.append(Paragraph("Backend Architecture, Multi-Agent Workflow & Complete File-by-File Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_teal, spaceAfter=14))

    meta_data = [
        [
            Paragraph("<b>System:</b> GlobeTrotter AI Core Backend", body_style),
            Paragraph("<b>Target Cadence:</b> 200 Articles / 24 Hours", body_style)
        ],
        [
            Paragraph("<b>Frameworks:</b> FastAPI, LangGraph, SQLAlchemy", body_style),
            Paragraph("<b>AI Provider:</b> NVIDIA NIM (Nemotron-3.5-Bolt)", body_style)
        ],
        [
            Paragraph("<b>Database:</b> PostgreSQL (PostGIS / pgvector ready)", body_style),
            Paragraph("<b>Caching:</b> In-Memory TTLCache (< 0.1ms latency)", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # SECTION 1: ARCHITECTURE OVERVIEW
    story.append(Paragraph("1. System Architecture Overview", h1_style))
    story.append(Paragraph(
        "GlobeTrotter AI is an autonomous, research-backed travel publishing engine capable of discovering, "
        "investigating, composing, optimizing, fact-checking, and publishing comprehensive tourism guides. "
        "The backend is structured into four decoupled layers: (1) <b>Application Core & Networking</b>, "
        "(2) <b>PostgreSQL Relational Persistence</b>, (3) <b>Domain Services & Telemetry</b>, and "
        "(4) <b>LangGraph Multi-Agent Pipeline</b>.", body_style
    ))
    story.append(Paragraph(
        "Every 432 seconds (7.2 minutes), the autonomous scheduler triggers a full multi-agent cycle across "
        "10 global regions and 13 tourism categories. The system incorporates two-tier duplicate prevention, "
        "strict 11-dimension quality gating (>= 8.0/10), and an in-memory micro-cache serving over 1,000,000 "
        "readers with sub-millisecond response times.", body_style
    ))
    story.append(Spacer(1, 10))

    # SECTION 2: ROOT & CORE APPLICATION FILES
    story.append(Paragraph("2. Root Application & Core Layer", h1_style))

    files_core = [
        ("app/main.py", "FastAPI Entrypoint", 
         "Initializes FastAPI instance, attaches CORS middleware (allowing cross-origin and multi-port frontend requests), "
         "manages application lifespan (runs ensure_database_exists() on startup), and mounts all modular routers under /api/v1."),
        
        ("app/config.py", "Settings & Environment", 
         "Pydantic BaseSettings class loading configuration from .env. Contains automatic URL sanitization to convert reserved "
         "password characters (such as '#' to '%23') preventing SQLAlchemy crashes, and exposes get_settings() as an lru_cache singleton."),
        
        ("app/llm.py", "NVIDIA NIM Client Factory", 
         "Configures the ChatNVIDIA provider interface pointing to https://integrate.api.nvidia.com/v1. Provides get_chat_llm() "
         "with configurable model names (nvidia/nemotron-3.5-bolt-e4b), temperature, timeouts, and token limits."),
        
        ("app/utils/logging.py", "Structured Logger", 
         "Custom unified logging facility that formats timestamps, log levels (INFO, WARNING, ERROR), and module identifiers "
         "consistently across background daemons, API requests, and LangGraph agent runs."),
    ]

    for fname, role, desc in files_core:
        story.append(Paragraph(f"• <b>{fname}</b> — <i>{role}</i>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 10))

    # SECTION 3: DATABASE LAYER
    story.append(Paragraph("3. Database & Persistence Layer (app/database/)", h1_style))

    files_db = [
        ("app/database/base.py", "SQLAlchemy Base", 
         "Declares the standard SQLAlchemy Base = declarative_base() parent class from which all database entities inherit."),
        
        ("app/database/session.py", "Engine & Connection Pool", 
         "Configures high-throughput connection pooling: pool_size=50, max_overflow=100, pool_timeout=10s, pool_recycle=1800s, "
         "and pool_pre_ping=True. Houses ensure_database_exists() which provisions the PostgreSQL database if missing, "
         "and get_db() providing transaction-scoped sessions per HTTP request."),
        
        ("app/database/models.py", "ORM Data Models", 
         "Contains all 6 database tables: Destination (regions & countries), Topic (canonical_key for deduplication), "
         "Article (full markdown guides, quality scores, word counts, SEO fields), ResearchSource (citations & URLs), "
         "ImageAsset (verified CC/public domain photos & licenses), and PublishingJob (idempotency tokens & delivery state)."),
        
        ("app/database/init_db.py", "Schema Provisioner", 
         "Executes Base.metadata.create_all(bind=engine) to verify or generate all indexes, foreign keys, and tables."),
        
        ("app/database/topic_store.py", "Topic Repository", 
         "Queries, saves, and dedupes topic pitches against existing database records using canonical hash lookups."),
    ]

    for fname, role, desc in files_db:
        story.append(Paragraph(f"• <b>{fname}</b> — <i>{role}</i>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 10))

    # SECTION 4: DOMAIN SERVICES LAYER
    story.append(Paragraph("4. Domain Services Layer (app/services/)", h1_style))

    files_serv = [
        ("app/services/discovery_service.py", "Topic Discovery", 
         "Uses NVIDIA NIM to discover off-the-beaten-path travel angles rotated across 10 regions (Asia, Europe, Americas, Africa) "
         "and 13 categories (Heritage, Natural Wonders, Food, Wildlife, etc.)."),
        
        ("app/services/research_service.py", "Factual Researcher", 
         "Queries Tavily Web Search API for opening hours, transport logistics, cultural context, and citation evidence. "
         "Includes automatic fallback to Wikipedia and Wikidata REST APIs if external search quota is unavailable."),
        
        ("app/services/writer_service.py", "Long-Form Writer", 
         "Directs NVIDIA NIM to author comprehensive 12-section editorial travel guides (800-1,500 words) with inline citations, "
         "practical traveler advice, and culturally respectful guidance."),
        
        ("app/services/seo_service.py", "SEO Optimization", 
         "Generates web-ready URL slugs, SEO title tags (<60 chars), meta descriptions (<160 chars), and primary focus keywords."),
        
        ("app/services/image_service.py", "Media Discovery", 
         "Searches Wikimedia Commons API (with Unsplash/Pexels fallbacks) for high-resolution photography with verified "
         "Creative Commons or Public Domain licensing, extracting author credit and license URLs."),
        
        ("app/services/evaluator_service.py", "Quality Gatekeeper", 
         "Evaluates articles on an 11-dimension rubric (factual accuracy, grammar, readability, depth, structure, image relevance). "
         "Calculates an overall quality score (1-10) and formulates corrective editorial guidance if revisions are needed."),
        
        ("app/services/publisher_service.py", "Publishing & Feeds", 
         "Handles single, batch, and selected article publishing. Enforces quality gates (with admin override support), assigns "
         "idempotency keys, purges RAM caches, and formats public blog payloads for web readers."),
        
        ("app/services/cache_service.py", "High-Concurrency Cache", 
         "Thread-safe in-memory TTLCache engine that computes SHA-256 ETags and delivers cached feed data in < 0.1ms directly from RAM."),
        
        ("app/services/scheduler_service.py", "24/7 Autopilot Daemon", 
         "Autonomous background thread executing 1 complete generation cycle every 432 seconds (7.2 minutes) to reach 200 articles/day. "
         "Handles daily midnight UTC rollovers, reset countdowns, and live status telemetry."),
    ]

    for fname, role, desc in files_serv:
        story.append(Paragraph(f"• <b>{fname}</b> — <i>{role}</i>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 10))

    # SECTION 5: LANGGRAPH MULTI-AGENT WORKFLOW
    story.append(Paragraph("5. LangGraph Multi-Agent Pipeline (app/graph/)", h1_style))

    files_graph = [
        ("app/graph/state.py", "Workflow State Definition", 
         "Defines WorkflowState (TypedDict) passed between nodes: stores topic metadata, research notes, markdown drafts, "
         "SEO tags, image assets, quality scores, revision feedback, and retry counters."),
        
        ("app/graph/workflow.py", "StateGraph Orchestrator", 
         "Builds the directed multi-agent graph with conditional edges. Implements should_revise_or_publish routing and exposes "
         "the top-level run_globetrotter_pipeline() function."),
        
        ("app/graph/nodes/duplicate_check.py", "Deduplication Node", 
         "Checks proposed topic angles against existing PostgreSQL topics using exact canonical key matching and semantic checks."),
        
        ("app/graph/nodes/research.py", "Research Node", 
         "Executes factual web research and stores citations and evidence in the graph state."),
        
        ("app/graph/nodes/writer.py", "Editorial Writer Node", 
         "Generates the full 12-section long-form article body and verifies word count compliance."),
        
        ("app/graph/nodes/seo.py", "SEO Generation Node", 
         "Produces slug, meta title, meta description, and keywords, updating the state."),
        
        ("app/graph/nodes/image_search.py", "Image Acquisition Node", 
         "Finds and attaches high-resolution licensed imagery and photographer attributions to the state."),
        
        ("app/graph/nodes/quality_check.py", "Quality Evaluation Node", 
         "Grades the article. If score >= 8.0, marks quality_passed and advances to publishing. If score < 8.0, triggers an automated "
         "self-revision pass. If retries expire without reaching 8.0, flags as needs_review."),
    ]

    for fname, role, desc in files_graph:
        story.append(Paragraph(f"• <b>{fname}</b> — <i>{role}</i>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 10))

    # SECTION 6: API ROUTES
    story.append(Paragraph("6. REST API Routing Layer (app/api/routes/)", h1_style))

    endpoints_data = [
        [Paragraph("<b>Route File</b>", body_style), Paragraph("<b>Key Endpoints</b>", body_style), Paragraph("<b>Functionality</b>", body_style)],
        [
            Paragraph("<b>health.py</b>", body_style),
            Paragraph("GET /health", code_style),
            Paragraph("Verifies backend readiness and PostgreSQL connection pool status.", body_style)
        ],
        [
            Paragraph("<b>auth.py</b>", body_style),
            Paragraph("POST /auth/login<br/>GET /auth/verify", code_style),
            Paragraph("Issues and validates HMAC-SHA256 JWT tokens for administrative access.", body_style)
        ],
        [
            Paragraph("<b>publishing.py</b>", body_style),
            Paragraph("GET /publish/feed<br/>POST /publish/{id}<br/>POST /publish/batch/selected<br/>POST /publish/unpublish/{id}", code_style),
            Paragraph("Serves cached public feed (< 0.1ms), handles single/batch/selected article publishing, and unpublishing.", body_style)
        ],
        [
            Paragraph("<b>automation.py</b>", body_style),
            Paragraph("GET /automation/status<br/>POST /automation/start<br/>POST /automation/stop<br/>POST /automation/trigger", code_style),
            Paragraph("Controls and monitors the 24/7 autonomous 200 articles/day publishing engine.", body_style)
        ],
        [
            Paragraph("<b>articles.py</b>", body_style),
            Paragraph("GET /articles<br/>GET /articles/{id}<br/>DELETE /articles/{id}", code_style),
            Paragraph("Provides administrative CRUD operations, status filtering, and article deletion.", body_style)
        ],
        [
            Paragraph("<b>workflow.py</b>", body_style),
            Paragraph("POST /workflow/run", code_style),
            Paragraph("Allows manual, on-demand execution of the full LangGraph pipeline for custom topics.", body_style)
        ],
        [
            Paragraph("<b>topics.py, research.py,<br/>seo.py, images.py,<br/>evaluation.py</b>", body_style),
            Paragraph("POST /topics/discover<br/>POST /research/search<br/>POST /seo/generate<br/>POST /images/search<br/>POST /evaluation/score", code_style),
            Paragraph("Standalone endpoints allowing isolated testing and execution of individual agent capabilities.", body_style)
        ],
    ]

    ep_table = Table(endpoints_data, colWidths=[110, 160, 234])
    ep_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(ep_table)
    story.append(Spacer(1, 14))

    # SECTION 7: SUMMARY / LIFECYCLE
    story.append(Paragraph("7. Complete End-to-End Execution Flow", h1_style))
    story.append(Paragraph(
        "<b>Step 1 — Topic Discovery:</b> The daemon or user triggers a run. Discovery service rotates region/category and pitches an uncrowded travel angle.<br/>"
        "<b>Step 2 — Deduplication Gate:</b> Hashes destination + category + angle into a canonical key. Rejects existing duplicates immediately.<br/>"
        "<b>Step 3 — Factual Research:</b> Tavily searches verified web sources for real-world logistical details, opening hours, and cultural facts.<br/>"
        "<b>Step 4 — Long-Form Writing:</b> NVIDIA NIM generates a structured 12-section Markdown guide with inline citations.<br/>"
        "<b>Step 5 — SEO & Media:</b> Generates search-optimized slugs and meta tags; retrieves public domain photography with attributions.<br/>"
        "<b>Step 6 — Quality Evaluation & Self-Correction:</b> Graded against an 11-dimension rubric. If below 8.0, passes through targeted revision.<br/>"
        "<b>Step 7 — High-Speed Publishing:</b> Saves article to PostgreSQL, transitions status to 'published', purges micro-caches, and streams to readers.",
        body_style
    ))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {filename}")

if __name__ == "__main__":
    build_pdf()
