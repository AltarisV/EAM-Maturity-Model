import streamlit as st
import pandas as pd
import altair as alt
import io
import json
import random
import re
from datetime import datetime
from io import BytesIO

# Optional imports for export
try:
    from docx import Document
    from docx.shared import Inches

    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False

import matplotlib.pyplot as plt

st.set_page_config(page_title="EAM Reifegrad-Assessment", layout="wide")

st.title("EAM Reifegrad-Assessment")

st.markdown("""
This assessment is based on a maturity model for Enterprise Architecture Management (EAM).

For each dimension and phase of the ADM, criteria are shown that are assigned to a specific maturity level:

- If **all criteria** of a level and the levels below are met, this level is considered the **Baseline**.
- The highest level in which **at least one criterion** is met is considered the **Ceiling**.
- The actual maturity lies somewhere between the Baseline and the Ceiling.
- Within this range, the next steps to improve the Enterprise Architecture of the company should be planned (starting from the lowest level).

Please check all criteria that your organization currently meets.
""")


# ------------------------------
# Daten laden
# ------------------------------
@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=';', encoding='utf-8-sig')
    # Dimensionen und Phasen auffüllen
    df["Dimension"] = df["Dimension"].ffill()
    df["ADM-Phases"] = df.groupby("Dimension")["ADM-Phases"].ffill().fillna("")
    # Numerische Stufe extrahieren
    df["level_num"] = df["Maturity Level"].str.extract(r"(\d+)").astype(int)
    # Level 0 ausblenden (keine Auswahl)
    df = df[df["level_num"] > 0].copy()
    return df


try:
    raw = load_data("Reifegradmodell.csv")
except Exception as e:
    st.error(f"Fehler beim Laden der CSV: {e}")
    st.stop()

# Gruppierte Kriterien je (Dimension, Phase, Level)
criteria = (
    raw.groupby(["Dimension", "ADM-Phases", "level_num"])['Description']
        .apply(list)
        .reset_index()
)

# Reihenfolge der Phasen definieren
phase_order = [
    "Preliminary",
    "A – Architecture Vision",
    "B, C, D – Business, Information Systems and Technology Architecture",
    "E – Opportunities & Solutions",
    "F – Migration Planning",
    "G – Implementation Governance",
    "H – Architecture Change Management",
    ""  # für Architecture Requirements Management ohne Phase
]
label_order = [
    "Preliminary",
    "A – Architecture Vision",
    "B, C, D – Business, Information Systems and Technology Architecture",
    "E – Opportunities & Solutions",
    "F – Migration Planning",
    "G – Implementation Governance",
    "H – Architecture Change Management",
    "Architecture Requirements Management"
]

criteria["phase_order"] = criteria["ADM-Phases"].apply(
    lambda x: phase_order.index(x) if x in phase_order else len(phase_order))
criteria = criteria.sort_values(["phase_order", "level_num"]).reset_index(drop=True)

# ------------------------------
# Hilfsfunktionen für Zustand, Auswertung & Export
# ------------------------------
RESP_KEY_PREFIX = "chk"

# Gewichtung für Zufalls-Ausfüllen je Level (1 sehr oft … 5 selten)
LEVEL_FILL_PROB = {1: 0.90, 2: 0.80, 3: 0.50, 4: 0.10, 5: 0.02}


def fill_probability(level: int) -> float:
    return LEVEL_FILL_PROB.get(int(level), 0.50)


def checkbox_key(group_idx: int, crit_idx: int) -> str:
    return f"{RESP_KEY_PREFIX}_{group_idx}_{crit_idx}"


def init_state_if_missing():
    # Initialisiere Checkbox-Keys, falls nicht vorhanden
    for g_idx, row in criteria.iterrows():
        for c_idx, _ in enumerate(row["Description"]):
            k = checkbox_key(g_idx, c_idx)
            if k not in st.session_state:
                st.session_state[k] = False


def collect_responses() -> pd.DataFrame:
    records = []
    for g_idx, row in criteria.iterrows():
        dim, phase, lvl = row["Dimension"], row["ADM-Phases"], row["level_num"]
        for c_idx, desc in enumerate(row["Description"]):
            k = checkbox_key(g_idx, c_idx)
            records.append({
                "Dimension": dim,
                "ADM-Phases": phase,
                "level_num": lvl,
                "Description": desc,
                "Checked": bool(st.session_state.get(k, False)),
            })
    return pd.DataFrame(records)


def summarize(responses_df: pd.DataFrame):
    # Aggregiere je (Dimension, Phase, Level)
    grp = (responses_df.groupby(["Dimension", "ADM-Phases", "level_num"])
           .agg(total=("Checked", "count"), done=("Checked", "sum"))
           .reset_index())
    grp["fulfilled"] = grp["done"] == grp["total"]
    grp["any"] = grp["done"] > 0

    # Ergebnisse pro (Dimension, Phase)
    results = []
    for (dim, phase), sub in grp.groupby(["Dimension", "ADM-Phases"]):
        base = 0
        for k in sorted(sub["level_num"].unique()):
            # alle Level <= k müssen vollständig erfüllt sein
            if sub.loc[sub["level_num"] <= k, "fulfilled"].all():
                base = k
        deckel = sub.loc[sub["any"], "level_num"].max() if sub["any"].any() else 0
        results.append({
            "Dimension": dim,
            "ADM-Phases": phase,
            "Baseline": base,
            "Deckel": deckel,
        })

    df_res = pd.DataFrame(results)
    df_res["Durchschnitt"] = (df_res["Baseline"] + df_res["Deckel"]) / 2
    df_res["Label"] = df_res.apply(lambda r: r["ADM-Phases"] if r["ADM-Phases"] else r["Dimension"], axis=1)
    df_res["Label"] = pd.Categorical(df_res["Label"], categories=label_order, ordered=True)
    df_res = df_res.sort_values("Label").reset_index(drop=True)
    return df_res, grp


def build_next_steps(df_res: pd.DataFrame, grp_levels: pd.DataFrame, responses_df: pd.DataFrame) -> pd.DataFrame:
    # Erstelle Next Steps je Phase: nicht erfüllte Kriterien zwischen Baseline+1 .. Deckel (oder Level 1, wenn noch nichts erfüllt)
    next_rows = []
    for _, r in df_res.iterrows():
        dim, phase, base, deckel = r["Dimension"], r["ADM-Phases"], r["Baseline"], r["Deckel"]
        if deckel == 0:
            target_levels = [1]
        else:
            target_levels = list(range(max(1, base + 1), deckel + 1))

        for lvl in target_levels:
            crits = responses_df[(responses_df["Dimension"] == dim) &
                                 (responses_df["ADM-Phases"] == phase) &
                                 (responses_df["level_num"] == lvl)]
            if crits.empty:
                continue
            for _, row in crits.iterrows():
                if not row["Checked"]:
                    next_rows.append({
                        "Dimension": dim,
                        "ADM-Phases": phase if phase else "(ohne Phase)",
                        "Level": int(lvl),
                        "ToDo": row["Description"],
                    })

    df_next = pd.DataFrame(next_rows).sort_values(["Dimension", "ADM-Phases", "Level"]).reset_index(drop=True)
    return df_next


def generate_chart_image(df_res: pd.DataFrame) -> BytesIO:
    """Render a compact chart with numeric indices on the x-axis for readability.
    The detailed mapping is provided in a table below the chart in the DOCX.
    """
    fig, ax = plt.subplots(figsize=(10, 4))

    # Numeric indices to avoid long, rotated labels
    x = list(range(1, len(df_res) + 1))
    baseline = df_res["Baseline"].tolist()
    deckel = df_res["Deckel"].tolist()

    ax.plot(x, baseline, marker="o", label="Baseline")
    ax.plot(x, deckel, marker="o", label="Deckel")

    ax.set_xticks(x)
    ax.set_xticklabels([str(i) for i in x])
    ax.set_ylabel("Level")
    ax.set_xlabel("Index (see table below)")
    ax.legend()
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=200)
    plt.close(fig)
    buf.seek(0)
    return buf


# ------------------------------
# Markdown → DOCX (bold + bullets + linebreaks)
# ------------------------------

def _add_runs_with_markdown(paragraph, text: str):
    """Add runs to a python-docx paragraph, interpreting **bold** segments."""
    parts = re.split(r"(\*\*.*?\*\*)", text)
    for part in parts:
        if part == "":
            continue
        if part.startswith("**") and part.endswith("**") and len(part) >= 4:
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        else:
            paragraph.add_run(part)


def add_markdownish_text(doc, text: str):
    """Render a small subset of Markdown-like text into python-docx:
    - Empty lines → new paragraph
    - Lines starting with '- ' → bullet list paragraphs
    - '**bold**' → bold runs
    """
    for raw_line in text.split("\n"):
        line = raw_line.rstrip("\r")
        if line.strip() == "":
            doc.add_paragraph("")
            continue
        if line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            _add_runs_with_markdown(p, line[2:])
        else:
            p = doc.add_paragraph()
            _add_runs_with_markdown(p, line)


def build_docx_report(df_res: pd.DataFrame, responses_df: pd.DataFrame) -> BytesIO:
    if not DOCX_AVAILABLE:
        raise RuntimeError("python-docx ist nicht installiert.")

    doc = Document()

    # Titel
    doc.add_heading('EAM Maturity Assessment', level=1)
    doc.add_paragraph(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Einleitung (Original-Text als Markdown-ähnliche Blöcke, inkl. Bold & Bullets)
    intro_md = (
        "This assessment is based on a maturity model for Enterprise Architecture Management (EAM).\n\n"
        "For each dimension and phase of the ADM, criteria are shown that are assigned to a specific maturity level:\n\n"
        "- If **all criteria** of a level and the levels below are met, this level is considered the **Baseline**.\n"
        "- The highest level in which **at least one criterion** is met is considered the **Ceiling**.\n"
        "- The actual maturity lies somewhere between the Baseline and the Ceiling.\n"
        "- Within this range, the next steps to improve the Enterprise Architecture of the company should be planned (starting from the lowest level).\n\n"
        "Please check all criteria that your organization currently meets."
    )
    add_markdownish_text(doc, intro_md)

    # Diagramm
    doc.add_heading('Maturity Overview', level=2)
    chart_png = generate_chart_image(df_res)
    doc.add_picture(chart_png, width=Inches(6.5))

    # Tabelle unter der Grafik (Index-Mapping)
    doc.add_paragraph("Indices on the chart correspond to the first column (#) in the table below.")
    table = doc.add_table(rows=1, cols=5)
    hdr = table.rows[0].cells
    hdr[0].text = "#"
    hdr[1].text = "Phase / Dimension"
    hdr[2].text = "Baseline"
    hdr[3].text = "Ceiling"
    hdr[4].text = "Average"

    for i, r in enumerate(df_res.itertuples(index=False), 1):
        row_cells = table.add_row().cells
        row_cells[0].text = str(i)
        row_cells[1].text = str(getattr(r, 'Label'))
        row_cells[2].text = str(int(getattr(r, 'Baseline')))
        row_cells[3].text = str(int(getattr(r, 'Deckel')))
        row_cells[4].text = f"{float(getattr(r, 'Durchschnitt')):.1f}"

    # Abschnitt pro Phase/Dimension
    doc.add_heading('Details & Next Steps', level=2)
    for _, r in df_res.iterrows():
        label = str(r['Label'])
        dim = r['Dimension']
        phase = r['ADM-Phases']
        baseline = int(r['Baseline'])
        deckel = int(r['Deckel'])

        doc.add_heading(label, level=3)
        p = doc.add_paragraph()
        p.add_run("Baseline: ").bold = True
        p.add_run(str(baseline))
        p.add_run("; Ceiling: ").bold = True
        p.add_run(str(deckel))

        # Nächstes Ziel-Level bestimmen (nur Baseline+1, wie besprochen)
        target_level = max(1, baseline + 1)
        if deckel > 0 and target_level > deckel:
            target_level = baseline + 1

        # Kriterien für das Ziel-Level, nur unerfüllte
        crits = responses_df[(responses_df["Dimension"] == dim) &
                             (responses_df["ADM-Phases"] == phase) &
                             (responses_df["level_num"] == target_level)]
        unmet = crits[~crits["Checked"]]

        doc.add_paragraph(f"To reach Level {target_level}, the following criteria must be met:")
        if unmet.empty:
            doc.add_paragraph(
                "All criteria for the immediate next level appear to be already met or no criteria are defined.")
        else:
            for _, row in unmet.iterrows():
                doc.add_paragraph(row['Description'], style="List Bullet")

    out = BytesIO()
    doc.save(out)
    out.seek(0)
    return out


# ------------------------------
# Seitenleiste: Testfunktionen, Chart & Export
# ------------------------------
with st.sidebar:
    st.subheader("Testfunktionen")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🎲 Zufällig ausfüllen"):
            init_state_if_missing()
            for g_idx, row in criteria.iterrows():
                lvl = int(row["level_num"])
                p = fill_probability(lvl)
                for c_idx, _ in enumerate(row["Description"]):
                    st.session_state[checkbox_key(g_idx, c_idx)] = random.random() < p
            st.rerun()
    with col_b:
        if st.button("↩︎ Zurücksetzen"):
            for k in list(st.session_state.keys()):
                if k.startswith(RESP_KEY_PREFIX + "_"):
                    st.session_state[k] = False
            st.rerun()

# ------------------------------
# UI: Checklisten rendern
# ------------------------------
init_state_if_missing()
for g_idx, row in criteria.iterrows():
    dim, phase, level = row["Dimension"], row["ADM-Phases"], row["level_num"]

    header = f"{dim} – {phase} – Level {level}" if phase else f"{dim} – Level {level}"

    with st.expander(header, expanded=False):
        for c_idx, desc in enumerate(row["Description"]):
            k = checkbox_key(g_idx, c_idx)
            if c_idx == 0:
                col1, col2 = st.columns([20,1])
                with col1:
                    st.checkbox(desc, key=k)
                with col2:
                    with st.popover("ℹ️"):
                        st.write("This level ensures objectives and risks are evaluated.")
            else:
                st.checkbox(desc, key=k)

# ------------------------------
# Auswertung & Visualisierung
# ------------------------------
responses_df = collect_responses()
df_res, grp_levels = summarize(responses_df)

# Chart in Sidebar (Altair)
chart = alt.Chart(df_res).transform_fold(
    fold=["Baseline", "Deckel"],
    as_=["Metric", "Level"]
).mark_line(point=True).encode(
    x=alt.X("Label:N", title="Phase / Dimension", sort=label_order),
    y=alt.Y("Level:Q", title="Level"),
    color=alt.Color("Metric:N", title="Kennzahl"),
    tooltip=[
        alt.Tooltip("Label:N", title="Phase/Dimension"),
        alt.Tooltip("Metric:N", title="Kennzahl"),
        alt.Tooltip("Level:Q", title="Level")
    ]
)
with st.sidebar:
    st.subheader("Maturity-Chart")
    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")
    st.subheader("Export")
    if not DOCX_AVAILABLE:
        st.info("`python-docx` ist nicht installiert. Bitte ausführen: `pip install python-docx`.")
    else:
        if st.button("📄 DOCX-Report erstellen"):
            try:
                docx_buf = build_docx_report(df_res, responses_df)
                st.download_button(
                    label="📥 Download DOCX",
                    data=docx_buf.getvalue(),
                    file_name=f"eam_reifegrad_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            except Exception as e:
                st.error(f"Fehler beim Erstellen des DOCX: {e}")

# Hauptbereich: Tabellen
st.subheader("Bewertungsergebnisse")
st.dataframe(df_res, use_container_width=True)

st.subheader("Nächste Schritte")
df_next = build_next_steps(df_res, grp_levels, responses_df)
if df_next.empty:
    st.success(
        "Alle Kriterien in den relevanten Bereichen sind erfüllt – keine offenen Next Steps im Baseline–Deckel-Bereich.")
else:
    st.dataframe(df_next, use_container_width=True)

# Glossar zuletzt (optional im Hauptbereich)
with st.expander("ℹ️ Glossar / Erklärungen"):
    glossary = {
        "Baseline": "Höchstes Level, bei dem alle Kriterien bis einschließlich dieses Levels erfüllt sind.",
        "Deckel": "Höchstes Level, bei dem mindestens ein Kriterium erfüllt ist (Ceiling).",
        "EAM": "Enterprise Architecture Management – ganzheitliche Planung und Steuerung der Unternehmensarchitektur.",
        "ADM": "Architecture Development Method – Vorgehensmodell aus TOGAF mit Phasen von Preliminary bis H.",
        "Architecture Requirements Management": "Querschnittsprozess, der Anforderungen über alle Phasen steuert.",
    }
    term = st.selectbox("Begriff auswählen", options=["(bitte wählen)"] + list(glossary.keys()))
    if term != "(bitte wählen)":
        st.markdown(f"**{term}:** {glossary[term]}")
