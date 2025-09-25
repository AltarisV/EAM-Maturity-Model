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
        "no_next": "All criteria within the relevant range are fulfilled – no open Next Steps within the Baseline–Ceiling range.",
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

- Wenn **alle Kriterien** eines Levels und der darunterliegenden Levels erfüllt sind, gilt dieses Level als **Baseline**.
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
        "no_next": "Alle Kriterien in den relevanten Bereichen sind erfüllt – keine offenen Next Steps im Baseline–Ceiling-Bereich.",
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

# Probabilities for the “fill randomly” helper per maturity level.
LEVEL_FILL_PROB = {1: 0.90, 2: 0.80, 3: 0.50, 4: 0.10, 5: 0.02}
