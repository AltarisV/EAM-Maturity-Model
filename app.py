import streamlit as st
import pandas as pd
import altair as alt

st.title("EAM Maturity Assessment")

# Daten laden
df = pd.read_csv(
    "Reifegradmodell.csv",
    sep=";",
    encoding="utf-8-sig"
)

# Dimensionen und Phasen auffüllen
df["Dimension"] = df["Dimension"].ffill()
df["ADM-Phases"] = df.groupby("Dimension")["ADM-Phases"].ffill().fillna("")

# Numerische Stufe extrahieren
df["level_num"] = df["Maturity Level"].str.extract(r"(\d+)").astype(int)

# Kriterien gruppieren
criteria = (
    df.groupby(["Dimension", "ADM-Phases", "level_num"])
    ["Description"]
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
    ""  # für Architektur Requirements Management ohne Phase
]
# Labels für X-Achse in der richtigen Reihenfolge
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

# Sortiere Kriterien nach Phase und Level
criteria["phase_order"] = criteria["ADM-Phases"].apply(lambda x: phase_order.index(x) if x in phase_order else len(phase_order))
criteria = criteria.sort_values(["phase_order", "level_num"]).reset_index(drop=True)

# Benutzerantworten sammeln
responses = {}
for idx, row in criteria.iterrows():
    dim, phase, level = row["Dimension"], row["ADM-Phases"], row["level_num"]
    header = f"{dim}"
    if phase:
        header += f" – {phase}"
    header += f" – Level {level}"
    st.subheader(header)
    checks = []
    for i, desc in enumerate(row["Description"]):
        key = f"chk_{idx}_{i}"
        checks.append(st.checkbox(desc, key=key))
    responses[(dim, phase, level)] = checks

# Auswertung vorbereiten
resp_df = pd.DataFrame([
    {"Dimension": d, "ADM-Phases": p, "level_num": lvl,
     "fulfilled": all(vals), "any": any(vals)}
    for (d, p, lvl), vals in responses.items()
])
results = []
for (dim, phase), grp in resp_df.groupby(["Dimension", "ADM-Phases"]):
    max_fulfilled = grp.loc[grp["fulfilled"], "level_num"].max() if grp["fulfilled"].any() else 0
    max_any       = grp.loc[grp["any"], "level_num"].max()       if grp["any"].any()       else 0
    results.append({
        "Dimension": dim,
        "ADM-Phases": phase,
        "Baseline": max_fulfilled,
        "Deckel": max_any
    })

# DataFrame mit Ergebnissen
df_res = pd.DataFrame(results)
df_res["Durchschnitt"] = (df_res["Baseline"] + df_res["Deckel"]) / 2

# Labels und Sortierung anpassen
df_res["Label"] = df_res.apply(
    lambda r: r["ADM-Phases"] if r["ADM-Phases"] else r["Dimension"], axis=1
)
df_res["Label"] = pd.Categorical(df_res["Label"], categories=label_order, ordered=True)
df_res = df_res.sort_values("Label").reset_index(drop=True)

# Chart erstellen
chart = alt.Chart(df_res).transform_fold(
    fold=["Baseline", "Deckel"],
    as_=["Metric", "Level"]
).mark_line(point=True).encode(
    x=alt.X("Label:N", title="Phase / Dimension", sort=label_order),
    y=alt.Y("Level:Q", title="Level"),
    color=alt.Color("Metric:N", title="Metric"),
    tooltip=[alt.Tooltip("Label:N"), alt.Tooltip("Metric:N"), alt.Tooltip("Level:Q")]
)

# Chart in Sidebar
with st.sidebar:
    st.subheader("Maturity Chart")
    st.altair_chart(chart, use_container_width=True)

# Hauptbereich: Tabelle der Ergebnisse
st.subheader("Bewertungsergebnisse")
st.dataframe(df_res)
