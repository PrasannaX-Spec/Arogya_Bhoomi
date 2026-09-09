"""
Generate Arogya Bhoomi — System Architecture & Workflow PDF
Uses ReportLab to produce a professional multi-page document.
"""
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Nirmula_System_Architecture.pdf")

# ── Color Palette ──
C_PRIMARY = colors.HexColor('#1b4332')
C_ACCENT = colors.HexColor('#2d6a4f')
C_LIGHT_BG = colors.HexColor('#f4f8f5')
C_BORDER = colors.HexColor('#d8e6dc')
C_INNER = colors.HexColor('#e2ece9')
C_MUTED = colors.HexColor('#555555')
C_SUCCESS = colors.HexColor('#22c55e')
C_BLUE = colors.HexColor('#2563eb')
C_ORANGE = colors.HexColor('#f97316')
C_RED = colors.HexColor('#dc2626')
C_GRAY = colors.HexColor('#6b7280')
C_HEADER_BG = colors.HexColor('#2d6a4f')
C_WHITE = colors.white


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle('DocTitle', parent=styles['Heading1'],
        fontSize=22, leading=28, textColor=C_PRIMARY, fontName='Helvetica-Bold',
        spaceAfter=2, alignment=TA_CENTER))

    styles.add(ParagraphStyle('DocSubtitle', parent=styles['Normal'],
        fontSize=11, leading=15, textColor=C_ACCENT, fontName='Helvetica-Bold',
        spaceAfter=6, alignment=TA_CENTER))

    styles.add(ParagraphStyle('SectionNum', parent=styles['Heading2'],
        fontSize=14, leading=18, textColor=C_PRIMARY, fontName='Helvetica-Bold',
        spaceBefore=14, spaceAfter=8))

    styles.add(ParagraphStyle('SubSection', parent=styles['Heading3'],
        fontSize=11, leading=14, textColor=C_ACCENT, fontName='Helvetica-Bold',
        spaceBefore=8, spaceAfter=4))

    styles.add(ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=9.5, leading=13, fontName='Helvetica', alignment=TA_JUSTIFY))

    styles.add(ParagraphStyle('BodyBold', parent=styles['Normal'],
        fontSize=9.5, leading=13, fontName='Helvetica-Bold'))

    styles.add(ParagraphStyle('SmallBody', parent=styles['Normal'],
        fontSize=8.5, leading=12, fontName='Helvetica'))

    styles.add(ParagraphStyle('CodeBlock', parent=styles['Normal'],
        fontSize=8.5, leading=11, fontName='Courier', textColor=C_PRIMARY,
        leftIndent=12, spaceAfter=4))

    styles.add(ParagraphStyle('CellNormal', parent=styles['Normal'],
        fontSize=8.5, leading=11, fontName='Helvetica'))

    styles.add(ParagraphStyle('CellBold', parent=styles['Normal'],
        fontSize=8.5, leading=11, fontName='Helvetica-Bold'))

    styles.add(ParagraphStyle('CellHeader', parent=styles['Normal'],
        fontSize=8.5, leading=11, fontName='Helvetica-Bold', textColor=C_WHITE))

    styles.add(ParagraphStyle('Footer', parent=styles['Normal'],
        fontSize=7.5, leading=10, textColor=C_MUTED, alignment=TA_CENTER))

    styles.add(ParagraphStyle('Caption', parent=styles['Normal'],
        fontSize=8, leading=10, textColor=C_GRAY, fontName='Helvetica-Oblique',
        alignment=TA_CENTER, spaceAfter=6))

    return styles


def std_table_style(has_header=True):
    base = [
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_INNER),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    if has_header:
        base.append(('BACKGROUND', (0, 0), (-1, 0), C_HEADER_BG))
    return TableStyle(base)


def green_section_bar(text, styles):
    return Table(
        [[Paragraph(text, styles['SectionNum'])]],
        colWidths=[490],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), C_LIGHT_BG),
            ('BOX', (0, 0), (-1, -1), 1.2, C_ACCENT),
            ('PADDING', (0, 0), (-1, -1), 6),
        ])
    )


def build_pdf():
    s = build_styles()
    story = []

    # ══════════════════════════════════════════
    # COVER / TITLE
    # ══════════════════════════════════════════
    story.append(Spacer(1, 60))
    story.append(Paragraph("Arogya Bhoomi", s['DocTitle']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("System Architecture &amp; Workflow Document", s['DocSubtitle']))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="80%", thickness=2, color=C_ACCENT, spaceBefore=4, spaceAfter=10))
    story.append(Paragraph("SIH 2026 · Problem Statement 193", s['Caption']))
    story.append(Paragraph("Traceable Recovery &amp; Deployment of Micronutrient Compounds from Expired Pharmaceuticals", s['Caption']))
    story.append(Spacer(1, 20))

    gen_time = datetime.now().strftime("%d %B %Y, %H:%M")
    story.append(Paragraph(f"<b>Generated:</b> {gen_time}", s['Caption']))
    story.append(Spacer(1, 30))

    # Quick facts box
    facts = [
        [Paragraph("Technology", s['CellBold']), Paragraph("Python 3.10 · Flask · SQLite · ReportLab · Leaflet.js", s['CellNormal'])],
        [Paragraph("Test Suite", s['CellBold']), Paragraph("88 automated tests — 100% pass rate", s['CellNormal'])],
        [Paragraph("API Endpoints", s['CellBold']), Paragraph("24 REST endpoints", s['CellNormal'])],
        [Paragraph("Database Tables", s['CellBold']), Paragraph("8 SQLite tables", s['CellNormal'])],
        [Paragraph("Compounds", s['CellBold']), Paragraph("Ferrous Sulphate (Fe) · Zinc Sulphate (Zn) · Potassium Chloride (K)", s['CellNormal'])],
        [Paragraph("Deficiency Regions", s['CellBold']), Paragraph("29 mapped Indian states", s['CellNormal'])],
        [Paragraph("Demo Intake Records", s['CellBold']), Paragraph("45 illustrative pharmaceutical batches", s['CellNormal'])],
    ]
    t = Table(facts, colWidths=[120, 370])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), C_LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_INNER),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t)

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════
    story.append(green_section_bar("Table of Contents", s))
    story.append(Spacer(1, 10))

    toc_items = [
        "1. High-Level System Architecture",
        "2. Database Schema (8 Tables)",
        "3. Recovery Pipeline — 4-Stage Execution Flow",
        "4. Module Dependency Map",
        "5. Tamper-Evident Audit Chain Mechanism",
        "6. Rule-Based Dosage Calculation Logic",
        "7. Soil-Deficiency Matching Strategy",
        "8. API Endpoint Map (24 Endpoints)",
        "9. End-to-End User Workflow",
        "10. Project File Architecture",
    ]
    for item in toc_items:
        story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{item}", s['Body']))
        story.append(Spacer(1, 3))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 1. HIGH-LEVEL SYSTEM ARCHITECTURE
    # ══════════════════════════════════════════
    story.append(green_section_bar("1. High-Level System Architecture", s))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The platform follows a <b>4-layer architecture</b> separating concerns across Client, Presentation, Application, and Data layers. "
        "All layers communicate through the central Flask application controller (<b>app.py</b>), which orchestrates API routing, business module delegation, audit logging, and PDF generation.",
        s['Body']))
    story.append(Spacer(1, 10))

    # Architecture layers table
    arch_header = [
        Paragraph("Layer", s['CellHeader']),
        Paragraph("Components", s['CellHeader']),
        Paragraph("Responsibility", s['CellHeader']),
    ]
    arch_rows = [arch_header]
    arch_data = [
        ("🖥️ Client Layer", "Web Browser", "User interaction via HTTP requests and rendered HTML pages"),
        ("📄 Presentation Layer", "Jinja2 Templates\n(base.html, index.html, stock.html,\npipeline.html, dosage.html,\nsoil_map.html, about.html)", "Server-side HTML rendering, layout inheritance, sidebar navigation, dynamic content injection"),
        ("⚙️ Application Layer", "Flask app.py\n· Route Dispatcher\n· 24 REST API Endpoints\n· PDF Generator (ReportLab)\n· Audit Engine (SHA-256)\n· Startup Seeder", "HTTP routing, request handling, response formatting, business logic orchestration, PDF generation, audit chain management"),
        ("🧠 Business Logic Layer", "Python Modules\n· intake.py — Compliance\n· geolocation.py — Location\n· matching.py — Soil Match\n· dosage.py — Dosage Calc", "Encapsulated domain logic: whitelist validation, coordinate resolution, Haversine distance matching, severity-adjusted dosage calculation"),
        ("🗄️ Data Layer", "SQLite (app.db) — 8 tables\nJSON/CSV Reference Datasets", "Persistent storage for batches, matches, partners, audit events, retests. Static reference data for compounds, soil deficiency, dosage rates"),
    ]
    for layer, comp, resp in arch_data:
        arch_rows.append([
            Paragraph(layer, s['CellBold']),
            Paragraph(comp.replace('\n', '<br/>'), s['CellNormal']),
            Paragraph(resp, s['CellNormal']),
        ])
    t = Table(arch_rows, colWidths=[100, 175, 215])
    t.setStyle(std_table_style())
    story.append(t)
    story.append(Spacer(1, 8))

    # Data flow
    story.append(Paragraph("<b>Data Flow Summary:</b>", s['BodyBold']))
    flow_lines = [
        "Browser → Flask Route Dispatcher → Jinja2 Template → Rendered HTML → Browser",
        "Browser → Flask API Endpoint → Business Module → SQLite → JSON Response → Browser",
        "Flask Startup → init_db_schema() → seed_demo_partners() → seed_demo_matches_and_audit() → recompute_and_fix_audit_hashes()",
        "load_data.py → JSON/CSV Reference Files → SQLite (compound_reference, soil_deficiency, dosage_rates, intake_batches)",
    ]
    for fl in flow_lines:
        story.append(Paragraph(f"&nbsp;&nbsp;→ {fl}", s['SmallBody']))
        story.append(Spacer(1, 2))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 2. DATABASE SCHEMA
    # ══════════════════════════════════════════
    story.append(green_section_bar("2. Database Schema (8 Tables)", s))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The SQLite database (<b>app.db</b>) contains 8 tables. Four are seeded from reference datasets via <b>load_data.py</b>, "
        "and four are created at runtime by <b>app.py</b>'s <b>init_db_schema()</b>.",
        s['Body']))
    story.append(Spacer(1, 8))

    # Table descriptions
    db_tables = [
        ("compound_reference", "Seeded", "3 rows", "Approved single-compound whitelist (FeSO₄, ZnSO₄, KCl). Used by intake.py for exact-match compliance validation."),
        ("soil_deficiency", "Seeded", "29 rows", "State-level soil deficiency records. Each row contains deficient nutrients, usable compounds, and usable/not-usable status."),
        ("dosage_rates", "Seeded", "3 rows", "Base application rates, severity multipliers, foliar specs. Raw JSON stores the full ICAR dosage record per compound."),
        ("intake_batches", "Seeded", "45 rows", "Pharmaceutical batch intake ledger. Tracks batch ID, compound, quantity, source location, expiry, and compliance status."),
        ("matches", "Runtime", "Dynamic", "Soil-deficiency match records created by pipeline execution. Links batch → target state, dosage, partner assignment, and handoff."),
        ("partners", "Runtime", "6 rows", "Certified recovery partner facilities. Tracks name, type, location, supported compounds, capacity, and availability."),
        ("audit_events", "Runtime", "Dynamic", "SHA-256 hash-linked append-only audit events. Each event references the previous event's hash (or 'GENESIS' for the first)."),
        ("soil_retests", "Runtime", "Dynamic", "Post-deployment soil re-test monitoring records. Tracks before/after values, improvement, and feedback."),
    ]

    db_header = [Paragraph("Table", s['CellHeader']), Paragraph("Origin", s['CellHeader']),
                 Paragraph("Size", s['CellHeader']), Paragraph("Purpose", s['CellHeader'])]
    db_rows = [db_header]
    for name, origin, size, purpose in db_tables:
        db_rows.append([
            Paragraph(f"<b>{name}</b>", s['CellNormal']),
            Paragraph(origin, s['CellNormal']),
            Paragraph(size, s['CellNormal']),
            Paragraph(purpose, s['CellNormal']),
        ])
    t = Table(db_rows, colWidths=[105, 55, 55, 275])
    t.setStyle(std_table_style())
    story.append(t)
    story.append(Spacer(1, 8))

    # Relationships
    story.append(Paragraph("<b>Key Relationships:</b>", s['BodyBold']))
    rels = [
        "compound_reference ─validates→ intake_batches (compound_name exact match)",
        "compound_reference ─defines rates→ dosage_rates (compound_name lookup)",
        "intake_batches ─produces→ matches (batch_doc_id → batch_id)",
        "intake_batches ─tracks→ audit_events (batch_doc_id → batch_id)",
        "matches ─assigned to→ partners (assigned_partner_id → partner_id)",
        "matches ─monitors→ soil_retests (match_id → match_id)",
        "soil_deficiency ─target region→ matches (state → target_state)",
    ]
    for r in rels:
        story.append(Paragraph(f"&nbsp;&nbsp;• {r}", s['SmallBody']))
        story.append(Spacer(1, 1))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 3. RECOVERY PIPELINE
    # ══════════════════════════════════════════
    story.append(green_section_bar("3. Recovery Pipeline — 4-Stage Execution Flow", s))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The core of the platform is the <b>4-stage automated recovery pipeline</b>, triggered by "
        "<font face='Courier' color='#1b4332'>POST /api/process_batch/&lt;batch_id&gt;</font>. "
        "The pipeline is <b>idempotent</b> — re-running the same batch does not create duplicate records.",
        s['Body']))
    story.append(Spacer(1, 10))

    # Stage detail table
    stages = [
        ("STAGE 1\nIntake &\nCompliance", "intake.py\ncheck_compliance()", 
         "1. Fetch batch from intake_batches\n2. Exact-match compound_name against compound_reference\n3. Set compliance_status = 'Accepted' or 'Rejected'\n4. Audit: BATCH_LOGGED + COMPLIANCE_PASSED/REJECTED",
         "Pipeline STOPS if\nstatus = 'Rejected'.\nRejected batches\ncannot proceed."),
        ("STAGE 2\nGeolocation\nResolution", "geolocation.py\nresolve_location()",
         "1. Parse source_location ('City, State' or 6-digit pincode)\n2. If pincode → resolve via indiapins package\n3. If city → lookup in hardcoded city coordinate table\n4. Fallback → state centroid coordinates\n5. Output: latitude, longitude, district, state",
         "Resolution always\nsucceeds for demo\ndata cities. State\ncentroid fallback\nguarantees output."),
        ("STAGE 3\nSoil-Deficiency\nMatching", "matching.py\nfind_match()",
         "1. Check if source_state is 'usable' AND has compound → Same-State Match\n2. If not, scan all 29 states for compound compatibility\n3. Compute Haversine distance to each candidate state\n4. Select nearest candidate → Nearest Fallback Match\n5. Audit: MATCH_CREATED event recorded",
         "Pipeline STOPS if\nno eligible state\nis found for the\ncompound."),
        ("STAGE 4\nDosage\nRecommendation", "dosage.py\nget_dosage()",
         "1. Lookup compound in dosage_rates table\n2. If base_rate = NULL → Foliar spray path (FeSO₄)\n   Return foliar_spec string directly\n3. If base_rate exists → Soil application path\n   adjusted_rate = base_rate × severity_multiplier\n4. Audit: DOSAGE_GENERATED event recorded",
         "FeSO₄ NEVER uses\nkg/ha calculation.\nAlways returns\nfoliar spray spec."),
    ]

    stage_header = [
        Paragraph("Stage", s['CellHeader']),
        Paragraph("Module / Function", s['CellHeader']),
        Paragraph("Execution Steps", s['CellHeader']),
        Paragraph("Gate / Notes", s['CellHeader']),
    ]
    stage_rows = [stage_header]
    for stage, module, steps, gate in stages:
        stage_rows.append([
            Paragraph(stage.replace('\n', '<br/>'), s['CellBold']),
            Paragraph(module.replace('\n', '<br/>'), s['CellNormal']),
            Paragraph(steps.replace('\n', '<br/>'), s['CellNormal']),
            Paragraph(gate.replace('\n', '<br/>'), s['CellNormal']),
        ])
    t = Table(stage_rows, colWidths=[70, 90, 215, 115])
    t.setStyle(std_table_style())
    story.append(t)
    story.append(Spacer(1, 10))

    # Pipeline flow summary
    story.append(Paragraph("<b>Pipeline Flow Summary:</b>", s['BodyBold']))
    story.append(Spacer(1, 4))
    flow_text = (
        "Batch Selected → [Stage 1: Compliance] → Accepted? "
        "→ [Stage 2: Geolocation] → Coordinates Resolved "
        "→ [Stage 3: Matching] → Region Found? "
        "→ [Stage 4: Dosage] → Match + Dosage Saved to DB "
        "→ Audit Events Chained → ✅ Pipeline Complete → 📄 Download PDF"
    )
    story.append(Paragraph(flow_text, s['Body']))
    story.append(Spacer(1, 6))

    # Post-pipeline actions
    story.append(Paragraph("<b>Post-Pipeline Persistence:</b>", s['BodyBold']))
    post_actions = [
        "INSERT match record into matches table (origin = 'pipeline')",
        "Append BATCH_LOGGED audit event (prev_hash = 'GENESIS')",
        "Append COMPLIANCE_PASSED audit event (prev_hash = hash of event 1)",
        "Append MATCH_CREATED audit event (prev_hash = hash of event 2)",
        "Append DOSAGE_GENERATED audit event (prev_hash = hash of event 3)",
        "Each audit event's hash = SHA256(event_id | batch_id | type | timestamp | description | prev_hash)",
    ]
    for i, action in enumerate(post_actions, 1):
        story.append(Paragraph(f"&nbsp;&nbsp;{i}. {action}", s['SmallBody']))
    
    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 4. MODULE DEPENDENCY MAP
    # ══════════════════════════════════════════
    story.append(green_section_bar("4. Module Dependency Map", s))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The application follows a <b>controller → module → database</b> pattern. "
        "Business logic is encapsulated in four independent Python modules under <b>modules/</b>. "
        "The Flask controller (<b>app.py</b>) orchestrates module calls and manages cross-cutting concerns "
        "(audit logging, PDF generation, startup seeding).",
        s['Body']))
    story.append(Spacer(1, 10))

    dep_header = [
        Paragraph("Component", s['CellHeader']),
        Paragraph("File", s['CellHeader']),
        Paragraph("Key Functions", s['CellHeader']),
        Paragraph("Dependencies", s['CellHeader']),
    ]
    dep_rows = [dep_header]
    deps = [
        ("Flask Controller", "app.py\n(1981 lines)", "process_batch()\nrecord_audit_event()\nverify_audit_chain()\nget_report_data_for_batch()\ngenerate_acknowledgement_pdf_bytes()\ninit_db_schema()\nseed_demo_partners()\nseed_demo_matches_and_audit()", "intake.py\ngeolocation.py\nmatching.py\ndosage.py\nSQLite\nReportLab"),
        ("Compliance Engine", "modules/intake.py\n(106 lines)", "check_compliance(batch_doc_id)\nrun_all_pending()", "SQLite\n(compound_reference,\nintake_batches)"),
        ("Geolocation Resolver", "modules/geolocation.py\n(223 lines)", "resolve_location(location_string)\ndistance_km(loc1, loc2)\n_parse_location_string()\n_resolve_via_pincode()\n_resolve_via_city_lookup()", "indiapins (optional)\nHardcoded city coords\nState centroids"),
        ("Matching Engine", "modules/matching.py\n(146 lines)", "find_match(batch_doc_id)", "geolocation.py\nSQLite\n(soil_deficiency,\nintake_batches)"),
        ("Dosage Calculator", "modules/dosage.py\n(98 lines)", "get_dosage(compound, severity)", "SQLite\n(dosage_rates)"),
    ]
    for comp, fpath, funcs, dep in deps:
        dep_rows.append([
            Paragraph(comp, s['CellBold']),
            Paragraph(fpath.replace('\n', '<br/>'), s['CellNormal']),
            Paragraph(funcs.replace('\n', '<br/>'), s['CellNormal']),
            Paragraph(dep.replace('\n', '<br/>'), s['CellNormal']),
        ])
    t = Table(dep_rows, colWidths=[95, 95, 170, 130])
    t.setStyle(std_table_style())
    story.append(t)
    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════
    # 5. AUDIT CHAIN
    # ══════════════════════════════════════════
    story.append(green_section_bar("5. Tamper-Evident Audit Chain Mechanism", s))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Every pipeline execution generates a chronological chain of <b>hash-linked audit events</b> per batch. "
        "This is an <b>application-level tamper-evident mechanism</b> (not blockchain infrastructure). "
        "Each event's hash is computed from its own data plus the previous event's hash, forming an unbreakable chain.",
        s['Body']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Hash Formula:</b>", s['BodyBold']))
    story.append(Paragraph(
        "<font face='Courier' size='9'>SHA256( event_id | batch_id | event_type | timestamp | description | previous_hash )</font>",
        s['Body']))
    story.append(Spacer(1, 8))

    # Audit chain example
    story.append(Paragraph("<b>Example Chain for BATCH-ZI2026-1014:</b>", s['BodyBold']))
    story.append(Spacer(1, 4))
    audit_header = [
        Paragraph("Event", s['CellHeader']),
        Paragraph("Type", s['CellHeader']),
        Paragraph("Actor", s['CellHeader']),
        Paragraph("Previous Hash", s['CellHeader']),
        Paragraph("Computed Hash", s['CellHeader']),
    ]
    audit_rows = [audit_header]
    chain = [
        ("1", "BATCH_LOGGED", "Distributor Intake", "GENESIS", "SHA256(1|...)"),
        ("2", "COMPLIANCE_PASSED", "Compliance Engine", "hash(event 1)", "SHA256(2|...)"),
        ("3", "MATCH_CREATED", "Matching Engine", "hash(event 2)", "SHA256(3|...)"),
        ("4", "DOSAGE_GENERATED", "Dosage Engine", "hash(event 3)", "SHA256(4|...)"),
    ]
    for eid, etype, actor, prev, computed in chain:
        audit_rows.append([
            Paragraph(eid, s['CellNormal']),
            Paragraph(etype, s['CellBold']),
            Paragraph(actor, s['CellNormal']),
            Paragraph(prev, s['CellNormal']),
            Paragraph(computed, s['CellNormal']),
        ])
    t = Table(audit_rows, colWidths=[40, 120, 110, 110, 110])
    t.setStyle(std_table_style())
    story.append(t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Verification Process:</b>", s['BodyBold']))
    verify_steps = [
        "Fetch all audit_events for a batch, ordered by event_id ASC",
        "For event 1: verify previous_event_hash == 'GENESIS'",
        "Re-compute SHA256 hash using stored data fields",
        "Compare computed hash with stored event_hash — mismatch = TAMPERING",
        "For event N: verify previous_event_hash == event_hash of event (N-1)",
        "If all events pass: '✓ All recorded audit chain events verified'",
    ]
    for i, step in enumerate(verify_steps, 1):
        story.append(Paragraph(f"&nbsp;&nbsp;{i}. {step}", s['SmallBody']))
    
    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 6. DOSAGE CALCULATION
    # ══════════════════════════════════════════
    story.append(green_section_bar("6. Rule-Based Dosage Calculation Logic", s))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The platform uses a <b>Rule-Based Soil-Deficiency Dosage Adjustment Model</b>. "
        "It adjusts recommended base application rates according to deficiency severity tiers. "
        "This is a transparent, deterministic calculation — <b>not an AI/ML prediction</b>.",
        s['Body']))
    story.append(Spacer(1, 10))

    dos_header = [
        Paragraph("Compound", s['CellHeader']),
        Paragraph("Application Type", s['CellHeader']),
        Paragraph("Base Rate", s['CellHeader']),
        Paragraph("Low (×1.25)", s['CellHeader']),
        Paragraph("Medium (×1.0)", s['CellHeader']),
        Paragraph("High (×0.75)", s['CellHeader']),
    ]
    dos_rows = [dos_header]
    dos_data = [
        ("Zinc Sulphate (Zn)", "Soil Application", "37.5 kg/ha", "46.88 kg/ha", "37.50 kg/ha", "28.13 kg/ha"),
        ("Potassium Chloride (K)", "Soil Application", "30.0 kg/ha", "37.50 kg/ha", "30.00 kg/ha", "22.50 kg/ha"),
    ]
    for comp, apptype, base, low, med, high in dos_data:
        dos_rows.append([
            Paragraph(comp, s['CellBold']),
            Paragraph(apptype, s['CellNormal']),
            Paragraph(base, s['CellNormal']),
            Paragraph(low, s['CellNormal']),
            Paragraph(med, s['CellNormal']),
            Paragraph(high, s['CellNormal']),
        ])
    t = Table(dos_rows, colWidths=[110, 80, 65, 75, 75, 75])
    t.setStyle(std_table_style())
    story.append(t)
    story.append(Spacer(1, 8))

    # Ferrous Sulphate special case
    story.append(Paragraph("<b>Special Case — Ferrous Sulphate (Fe):</b>", s['SubSection']))
    story.append(Paragraph(
        "Ferrous Sulphate does <b>NOT</b> use soil kg/ha dosage. The base_rate_kg_ha is <b>NULL</b> in the database. "
        "Instead, it returns a <b>foliar spray specification</b> directly:",
        s['Body']))
    story.append(Spacer(1, 4))

    fe_box = Table(
        [[Paragraph(
            '<b>Foliar Guidance:</b> "3–4 sprays of 1.0% ferrous sulphate (FeSO₄, 20% Fe) at weekly intervals during peak vegetative stage."',
            s['CellNormal'])]],
        colWidths=[490],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), C_LIGHT_BG),
            ('BOX', (0, 0), (-1, -1), 1.5, C_BLUE),
            ('PADDING', (0, 0), (-1, -1), 8),
        ])
    )
    story.append(fe_box)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Severity Tier Interpretation:</b>", s['BodyBold']))
    story.append(Paragraph("• <b>Low</b> severity = higher deficiency in soil → <b>increased</b> dosage (+25%)", s['SmallBody']))
    story.append(Paragraph("• <b>Medium</b> severity = standard deficiency → base rate as-is", s['SmallBody']))
    story.append(Paragraph("• <b>High</b> severity = lower deficiency in soil → <b>reduced</b> dosage (−25%)", s['SmallBody']))
    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════
    # 7. MATCHING STRATEGY
    # ══════════════════════════════════════════
    story.append(green_section_bar("7. Soil-Deficiency Matching Strategy", s))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The matching engine pairs accepted pharmaceutical batches with Indian states that have documented soil deficiency "
        "for the batch's specific compound. It uses a <b>two-priority strategy</b>:",
        s['Body']))
    story.append(Spacer(1, 8))

    match_header = [
        Paragraph("Priority", s['CellHeader']),
        Paragraph("Match Type", s['CellHeader']),
        Paragraph("Logic", s['CellHeader']),
        Paragraph("Distance", s['CellHeader']),
    ]
    match_rows = [match_header]
    match_rows.append([
        Paragraph("1 (Highest)", s['CellBold']),
        Paragraph("Same-State Match", s['CellBold']),
        Paragraph("Source state is 'usable' AND compound is listed in usable_compounds for that state", s['CellNormal']),
        Paragraph("0 km\n(same state)", s['CellNormal']),
    ])
    match_rows.append([
        Paragraph("2 (Fallback)", s['CellBold']),
        Paragraph("Nearest Fallback Match", s['CellBold']),
        Paragraph("Scan ALL 29 states where status = 'usable'. Filter by compound compatibility. "
                   "Compute Haversine great-circle distance from source to each candidate. Select nearest.", s['CellNormal']),
        Paragraph("Haversine\ndistance (km)", s['CellNormal']),
    ])
    match_rows.append([
        Paragraph("—", s['CellNormal']),
        Paragraph("No Match", s['CellBold']),
        Paragraph("No usable state has the batch compound in its usable_compounds list. Pipeline stops.", s['CellNormal']),
        Paragraph("—", s['CellNormal']),
    ])
    t = Table(match_rows, colWidths=[70, 100, 240, 80])
    t.setStyle(std_table_style())
    story.append(t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Haversine Distance Formula:</b>", s['BodyBold']))
    story.append(Paragraph(
        "The Haversine formula computes great-circle distance between two latitude/longitude coordinate pairs "
        "using Earth's radius (6,371 km). This ensures the nearest-fallback match is geographically optimal.",
        s['Body']))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 8. API ENDPOINT MAP
    # ══════════════════════════════════════════
    story.append(green_section_bar("8. API Endpoint Map (24 Endpoints)", s))
    story.append(Spacer(1, 8))

    api_header = [
        Paragraph("Method", s['CellHeader']),
        Paragraph("Endpoint", s['CellHeader']),
        Paragraph("Purpose", s['CellHeader']),
    ]
    api_rows = [api_header]
    endpoints = [
        ("POST", "/api/process_batch/<id>", "Execute 4-stage recovery pipeline (idempotent)"),
        ("GET", "/api/batches", "List all intake batches"),
        ("POST", "/api/batches", "Register a new batch"),
        ("GET", "/api/batches/<id>", "Fetch single batch details"),
        ("POST", "/api/run_compliance", "Run compliance on all pending batches"),
        ("GET", "/api/matches", "List all soil-deficiency matches"),
        ("GET", "/api/matches/<id>", "Single match detail with explanation"),
        ("POST", "/api/matches/<id>/status", "Update match lifecycle status"),
        ("POST", "/api/matches/<id>/assign-partner", "Assign certified partner facility"),
        ("POST", "/api/matches/<id>/record-handoff", "Record material handoff completion"),
        ("GET", "/api/partners", "List all partner facilities"),
        ("GET", "/api/partners/<id>", "Single partner detail"),
        ("GET", "/api/partners/eligible", "Eligible partners with capacity checks"),
        ("GET", "/api/audit/<batch_id>", "Fetch audit timeline for a batch"),
        ("POST", "/api/audit/<batch_id>/verify", "Verify SHA-256 chain integrity"),
        ("GET", "/api/retests", "Soil re-test records &amp; statistics"),
        ("POST", "/api/retests", "Schedule a new soil re-test"),
        ("POST", "/api/retests/<id>/result", "Submit post-application re-test result"),
        ("GET", "/api/compounds", "Approved compound whitelist"),
        ("GET", "/api/soil_deficiency", "29-state soil deficiency data"),
        ("GET", "/api/stats", "Dashboard KPI statistics"),
        ("GET", "/api/network_data", "Map data (sources, targets, partners, flows)"),
        ("POST", "/api/simulate_recovery", "What-If dosage simulator"),
        ("GET", "/api/reports/pdf/<batch_id>", "Download acknowledgement PDF (eligible only)"),
    ]
    for method, endpoint, purpose in endpoints:
        color = '#22c55e' if method == 'GET' else '#2563eb'
        api_rows.append([
            Paragraph(f"<font color='{color}'><b>{method}</b></font>", s['CellNormal']),
            Paragraph(f"<font face='Courier' size='8'>{endpoint}</font>", s['CellNormal']),
            Paragraph(purpose, s['CellNormal']),
        ])
    t = Table(api_rows, colWidths=[45, 205, 240])
    t.setStyle(std_table_style())
    story.append(t)

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 9. USER WORKFLOW
    # ══════════════════════════════════════════
    story.append(green_section_bar("9. End-to-End User Workflow", s))
    story.append(Spacer(1, 8))

    wf_header = [
        Paragraph("Step", s['CellHeader']),
        Paragraph("Page / Route", s['CellHeader']),
        Paragraph("User Actions", s['CellHeader']),
        Paragraph("System Response", s['CellHeader']),
    ]
    wf_rows = [wf_header]
    workflow = [
        ("1", "📊 Dashboard\n/", "View platform overview", "Displays KPIs: total batches, accepted count, matched count, recovery rate, compounds processed"),
        ("2", "📦 Stock &amp; Compliance\n/stock", "Browse 45 intake records.\nSelect a batch.\nClick 'Run Pipeline'.", "Shows batch ledger with compound, quantity, source, expiry status. Navigates to /pipeline?batch=<id>"),
        ("3", "🔬 Recovery Pipeline\n/pipeline", "STEP 01: Select batch from dropdown.\nSTEP 02: Click 'RUN RECOVERY PIPELINE'.\nSTEP 03: View result.\nClick '📄 Download PDF'.", "7-step animated progress bar.\nExecutes 4-stage pipeline.\nDisplays match, dosage, partner.\nGenerates acknowledgement PDF."),
        ("4", "🧮 Dosage Calculator\n/dosage", "Select compound, enter quantity,\nchoose severity tier.\nClick 'Calculate'.", "Shows adjusted rate, elemental nutrient yield, addressable hectares, calculation breakdown."),
        ("5", "🗺️ Recovery Map\n/soil-map", "Pan/zoom interactive map.\nClick colored markers.\nView flow lines.", "29 element-color-coded markers.\nPopups with state deficiency profile.\nPartner pins and recovery flows."),
        ("6", "ℹ️ About\n/about", "Read methodology &amp; scope", "Chemical standards, regulatory references, system design, scope boundaries."),
    ]
    for step, page, actions, response in workflow:
        wf_rows.append([
            Paragraph(step, s['CellBold']),
            Paragraph(page.replace('\n', '<br/>'), s['CellBold']),
            Paragraph(actions.replace('\n', '<br/>'), s['CellNormal']),
            Paragraph(response.replace('\n', '<br/>'), s['CellNormal']),
        ])
    t = Table(wf_rows, colWidths=[30, 100, 165, 195])
    t.setStyle(std_table_style())
    story.append(t)
    story.append(Spacer(1, 10))

    # Recovery Map Legend
    story.append(Paragraph("<b>Recovery Map — Element Color Legend:</b>", s['BodyBold']))
    story.append(Spacer(1, 4))
    legend_data = [
        [Paragraph("🟢 Green (#22c55e)", s['CellBold']), Paragraph("Zinc (Zn) — Zinc Sulphate deficiency areas", s['CellNormal'])],
        [Paragraph("🔵 Blue (#2563eb)", s['CellBold']), Paragraph("Iron (Fe) — Ferrous Sulphate deficiency areas", s['CellNormal'])],
        [Paragraph("🟠 Orange (#f97316)", s['CellBold']), Paragraph("Potassium (K) — Potassium Chloride deficiency areas", s['CellNormal'])],
        [Paragraph("⚪ Gray (#6b7280)", s['CellBold']), Paragraph("Non-Usable Region — no approved compound match", s['CellNormal'])],
    ]
    t = Table(legend_data, colWidths=[145, 345])
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_INNER),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 10. PROJECT FILE ARCHITECTURE
    # ══════════════════════════════════════════
    story.append(green_section_bar("10. Project File Architecture", s))
    story.append(Spacer(1, 8))

    file_tree_lines = [
        ("SIH-193/", "", "Repository root"),
        ("├── README.md", "", "Master project documentation"),
        ("│", "", ""),
        ("└── starter_kit/starter/", "", "Application directory"),
        ("    ├── app.py", "80 KB", "Flask application &amp; REST API (1981 lines)"),
        ("    ├── app.db", "240 KB", "SQLite database (8 tables)"),
        ("    ├── load_data.py", "4 KB", "Database initializer &amp; seeder script"),
        ("    ├── requirements.txt", "—", "Python dependencies"),
        ("    │", "", ""),
        ("    ├── modules/", "", "Business Logic Modules"),
        ("    │   ├── intake.py", "3 KB", "Module 1: Whitelist &amp; Compliance (106 lines)"),
        ("    │   ├── geolocation.py", "10 KB", "Module 4: Geolocation Resolution (223 lines)"),
        ("    │   ├── matching.py", "6 KB", "Module 2: Soil Matching Engine (146 lines)"),
        ("    │   └── dosage.py", "3 KB", "Module 3: Rule-Based Dosage Calculator (98 lines)"),
        ("    │", "", ""),
        ("    ├── data/", "", "Authoritative Reference Datasets"),
        ("    │   ├── compound_list.json", "—", "3 approved single-compound salts"),
        ("    │   ├── soil_deficiency.json", "—", "29 state-level deficiency records"),
        ("    │   ├── dosage_table.json", "—", "ICAR GRD base rates &amp; adjustments"),
        ("    │   ├── demo_intake.csv", "—", "45 illustrative intake batch records"),
        ("    │   └── districts.json", "—", "Illustrative district layer"),
        ("    │", "", ""),
        ("    ├── templates/", "", "Jinja2 HTML Templates"),
        ("    │   ├── base.html", "—", "Master layout + sidebar navigation"),
        ("    │   ├── index.html", "—", "Dashboard"),
        ("    │   ├── stock.html", "—", "Stock &amp; Compliance Ledger"),
        ("    │   ├── pipeline.html", "—", "Recovery Pipeline + PDF Download"),
        ("    │   ├── dosage.html", "—", "Dosage Calculator / Simulator"),
        ("    │   ├── soil_map.html", "—", "Recovery Map (Leaflet.js, 29 markers)"),
        ("    │   └── about.html", "—", "Methodology &amp; System Specs"),
        ("    │", "", ""),
        ("    ├── static/", "", "CSS &amp; JavaScript Assets"),
        ("    │   ├── style.css", "—", "Custom CSS design system"),
        ("    │   └── script.js", "—", "Frontend interactivity"),
        ("    │", "", ""),
        ("    └── tests/", "", "Automated Test Suite (88 tests)"),
        ("        ├── test_intake.py", "", "Compliance validation tests"),
        ("        ├── test_geolocation.py", "", "Location resolution tests"),
        ("        ├── test_matching.py", "", "Soil matching tests"),
        ("        ├── test_dosage.py", "", "Dosage calculation tests"),
        ("        ├── test_pipeline.py", "", "End-to-end pipeline tests"),
        ("        ├── test_final_restructure.py", "", "Route, PDF, eligibility tests"),
        ("        ├── test_enhancements.py", "", "Enhancement feature tests"),
        ("        ├── test_phase2.py", "", "Phase 2 integration tests"),
        ("        ├── test_phase3.py", "", "Phase 3 match lifecycle tests"),
        ("        ├── test_phase4.py", "", "Phase 4 partner assignment tests"),
        ("        └── test_phase5.py", "", "Phase 5 audit &amp; re-test tests"),
    ]
    ft_header = [Paragraph("Path", s['CellHeader']), Paragraph("Size", s['CellHeader']), Paragraph("Description", s['CellHeader'])]
    ft_rows = [ft_header]
    for path, size, desc in file_tree_lines:
        ft_rows.append([
            Paragraph(f"<font face='Courier' size='7.5'>{path}</font>", s['CellNormal']),
            Paragraph(size, s['CellNormal']),
            Paragraph(desc, s['CellNormal']),
        ])
    t = Table(ft_rows, colWidths=[215, 45, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_HEADER_BG),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, C_INNER),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)

    # ── Footer ──
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph(
        "<b>Arogya Bhoomi</b> · Healthy Soil • Healthy Life · Smart India Hackathon (SIH) 2026 · Problem Statement 193",
        s['Footer']))
    story.append(Paragraph(
        f"System Architecture Document · Generated {gen_time}",
        s['Footer']))

    # ── Build PDF ──
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
        title="Arogya Bhoomi — System Architecture & Workflow",
        author="SIH 2026 Team",
    )
    doc.build(story)
    print(f"[OK] PDF generated successfully: {OUTPUT_PATH}")
    print(f"   Size: {os.path.getsize(OUTPUT_PATH):,} bytes")


if __name__ == "__main__":
    build_pdf()
