"""
config.py
Centralized constants and localization strings used across the app.
"""

RESP_KEY_PREFIX = "resp|"

translations = {
    "en": {
        "title": "EAM Maturity Assessment",
        "intro": """
This assessment is based on a maturity model for Enterprise Architecture Management (EAM).

For each dimension and phase of the ADM, criteria are shown that are assigned to a specific maturity level:

- If **all criteria** of a level and the levels below are met, this level is considered the **Baseline**. 
- The highest level in which **at least one criterion** is met is considered the **Ceiling**.
- The actual maturity lies somewhere between the Baseline and the Ceiling. 
- Within this range, the next steps to improve the Enterprise Architecture of the company should be planned (starting from the lowest level). 

Please check all criteria that your organization currently meets.
""",
        "sidebar_tests": "Test functions",
        "btn_random": "🎲 Fill randomly",
        "btn_reset": "↩︎ Reset",
        "sidebar_chart": "Maturity Chart",
        "export": "Export",
        "docx_info": "`python-docx` is not installed. Please run: `pip install python-docx`.",
        "btn_docx": "Create DOCX Report",
        "download_docx": "📥 Download DOCX",
        "btn_xlsx": "Create Excel",
        "download_xlsx": "📥 Download Excel",
        "results": "Assessment Results",
        "next_steps": "Next Steps",
        "no_next": "All criteria within the relevant range are fulfilled – no open Next Steps within the "
                   "Baseline–Ceiling range.",
        "glossary": "ℹ️ Glossary / Explanations",
        "select_term": "Select a term",
        "lang_select": "🌐 Language",
        "benefit_title": "Benefits of achieving this level",
        "chart-sidebar-heading": "Metric"
    },
    "de": {
        "title": "EAM Reifegrad-Assessment",
        "intro": """
Dieses Assessment basiert auf einem Reifegradmodell für Enterprise Architecture Management (EAM).

Für jede Dimension und Phase des ADM werden Kriterien angezeigt, die einem bestimmten Reifegrad-Level zugeordnet sind:

- Wenn **alle Kriterien** eines Levels und der darunterliegenden Levels erfüllt sind, gilt dieses Level als 
**Baseline**. 
- Das höchste Level, in dem **mindestens ein Kriterium** erfüllt ist, gilt als **Deckel** (Ceiling). 
- Die tatsächliche Reife liegt zwischen Baseline und Deckel. 
- Innerhalb dieses Bereichs sollten die nächsten Schritte zur Verbesserung der Unternehmensarchitektur geplant werden (beginnend beim niedrigsten Level). 

Bitte markieren Sie alle Kriterien, die Ihre Organisation aktuell erfüllt.
""",
        "sidebar_tests": "Testfunktionen",
        "btn_random": "🎲 Zufällig ausfüllen",
        "btn_reset": "↩︎ Zurücksetzen",
        "sidebar_chart": "Reifegrad-Diagramm",
        "export": "Export",
        "docx_info": "`python-docx` ist nicht installiert. Bitte ausführen: `pip install python-docx`.",
        "btn_docx": "DOCX-Report erstellen",
        "download_docx": "📥 DOCX herunterladen",
        "btn_xlsx": "Excel erstellen",
        "download_xlsx": "📥 Excel herunterladen",
        "results": "Bewertungsergebnisse",
        "next_steps": "Nächste Schritte",
        "no_next": "Alle Kriterien in den relevanten Bereichen sind erfüllt – keine offenen Next Steps im "
                   "Baseline–Ceiling-Bereich.",
        "glossary": "ℹ️ Glossar / Erklärungen",
        "select_term": "Begriff auswählen",
        "lang_select": "🌐 Sprache",
        "benefit_title": "Mehrwert des Erreichens dieses Levels",
        "chart-sidebar-heading": "Kennzahl"
    }
}

phase_order = [
    "Preliminary",
    "A – Architecture Vision",
    "B, C, D – Business, Information Systems and Technology Architecture",
    "E – Opportunities & Solutions",
    "F – Migration Planning",
    "G – Implementation Governance",
    "H – Architecture Change Management",
    ""  # Architecture Requirements Management
]

# --- Glossary UI labels ---
for _lang, t in translations.items():
    t.setdefault("glossary_search", "Search term" if _lang == "en" else "Begriff suchen")
    t.setdefault("glossary_lang_en", "English" if _lang == "en" else "Englisch")
    t.setdefault("glossary_lang_de", "German" if _lang == "en" else "Deutsch")
    t.setdefault("glossary_no_match", "No matching entries." if _lang == "en" else "Keine passenden Einträge.")

# --- Built-in bilingual glossary (used if glossary.csv not found) ---
GLOSSARY = {
    "Baseline": {
        "en": "Highest level where all criteria up to and including that level are fulfilled.",
        "de": "Höchstes Level, bei dem alle Kriterien bis einschließlich dieses Levels erfüllt sind.",
    },
    "Ceiling": {
        "en": "Highest level where at least one criterion is fulfilled.",
        "de": "Höchstes Level, in dem mindestens ein Kriterium erfüllt ist.",
    },
    "Baseline–Ceiling Range": {
        "en": "Span between Baseline and Ceiling; actual maturity lies within this interval.",
        "de": "Spanne zwischen Baseline und Deckel; die tatsächliche Reife liegt in diesem Bereich.",
    },
    "Next Steps": {
        "en": "Unmet criteria on the immediate next target level; concrete actions to progress maturity.",
        "de": "Nicht erfüllte Kriterien des unmittelbar nächsten Ziel-Levels; konkrete Schritte zur Erhöhung der Reife.",
    },
    "EAM": {
        "en": "Enterprise Architecture Management — holistic planning and governance of the enterprise architecture.",
        "de": "Enterprise Architecture Management — ganzheitliche Planung und Steuerung der Unternehmensarchitektur.",
    },
    "ADM": {
        "en": "Architecture Development Method (TOGAF) with phases from Preliminary to H.",
        "de": "Architecture Development Method (TOGAF) mit Phasen von Preliminary bis H.",
    },
    "ADM Phases": {
        "en": "Preliminary, A: Vision, B/C/D: Architectures, E: Solutions, F: Migration, G: Implementation Governance, H: Change.",
        "de": "Preliminary, A: Vision, B/C/D: Architekturen, E: Lösungen, F: Migration, G: Implementierungssteuerung, H: Veränderung.",
    },
    "Architecture Requirements Management": {
        "en": "Cross-cutting process that manages requirements across all ADM phases.",
        "de": "Querschnittsprozess zur Verwaltung von Anforderungen über alle ADM-Phasen.",
    },
    "Maturity Level": {
        "en": "Ordinal scale (e.g., 1–5) grouping criteria into progressive capability bands.",
        "de": "Ordinale Skala (z. B. 1–5), die Kriterien in aufeinander aufbauende Fähigkeitsstufen bündelt.",
    },
    "Capability": {
        "en": "Ability of an organization to achieve a specific outcome repeatedly and reliably.",
        "de": "Fähigkeit einer Organisation, ein bestimmtes Ergebnis wiederholt und verlässlich zu erzielen.",
    },
    "Gap Analysis": {
        "en": "Compares current and target architectures to identify required changes.",
        "de": "Vergleicht Ist- und Zielarchitektur, um notwendige Änderungen zu identifizieren.",
    },
    "Architecture Roadmap": {
        "en": "Sequenced plan of work packages and plateaus to reach target architecture.",
        "de": "Sequenzierter Plan aus Arbeitspaketen und Plateaus zur Erreichung der Zielarchitektur.",
    },
    "Plateaus & Gaps": {
        "en": "States (plateaus) and differences (gaps) used to plan transitions.",
        "de": "Zustände (Plateaus) und Differenzen (Gaps) zur Planung von Übergängen.",
    },
    "Work Package": {
        "en": "Deliverable unit of work that advances the roadmap.",
        "de": "Lieferobjekt/Arbeitseinheit, die die Roadmap vorantreibt.",
    },
    "Migration Planning": {
        "en": "Scheduling and dependency management of work packages across releases.",
        "de": "Zeitplanung und Abhängigkeitssteuerung von Arbeitspaketen über Releases.",
    },
    "Implementation Governance": {
        "en": "Ensures delivery is compliant with architecture principles and standards.",
        "de": "Sichert die liefernde Umsetzung gemäß Architekturprinzipien und -standards ab.",
    },
    "Architecture Principles": {
        "en": "Guiding rules for decision-making and solution design.",
        "de": "Leitplanken für Entscheidungen und Lösungsdesign.",
    },
    "Stakeholder": {
        "en": "Individual or group with interest or influence on the architecture.",
        "de": "Person oder Gruppe mit Interesse oder Einfluss auf die Architektur.",
    },
    "KPI": {
        "en": "Key Performance Indicator; metric to monitor outcomes and value.",
        "de": "Kennzahl zur Messung von Ergebnissen und Nutzen.",
    },
    "Heatmap": {
        "en": "Visual highlighting of status or risk across a matrix (e.g., capabilities × value).",
        "de": "Visuelle Hervorhebung von Status oder Risiko in einer Matrix (z. B. Fähigkeiten × Nutzen).",
    },
}

# Probabilities for the “fill randomly” helper per maturity level.
LEVEL_FILL_PROB = {1: 0.90, 2: 0.80, 3: 0.50, 4: 0.10, 5: 0.02}
