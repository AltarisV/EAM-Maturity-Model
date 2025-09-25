import streamlit as st
import core
import altair as alt
from datetime import datetime

from config import translations, phase_order, RESP_KEY_PREFIX
from core import (
    load_model, load_value_data, value_to_bullets, init_state_if_missing,
    checkbox_key, collect_responses, summarize, build_next_steps,
    fill_probability
)
from exports import DOCX_AVAILABLE, generate_chart_image, build_docx_report, generate_excel_report

st.set_page_config(page_title="EAM Maturity Assessment", layout="wide")

# ------------------------------
# Language toggle
# ------------------------------
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

with st.sidebar:
    st.markdown("### 🌐 Language / Sprache")
    btn_label = "🇬🇧 English" if st.session_state["lang"] == "en" else "🇩🇪 Deutsch"
    if st.button(btn_label, key="lang_toggle"):
        # snapshot all checkbox states so we can restore after language swap
        snap = {k: bool(v) for k, v in st.session_state.items() if isinstance(k, str) and k.startswith("resp|")}
        st.session_state["__resp_snapshot"] = snap
        st.session_state["lang"] = "de" if st.session_state["lang"] == "en" else "en"
        st.rerun()

lang = st.session_state["lang"]
texts = translations[lang]

# ------------------------------
# Data
# ------------------------------
try:
    raw = load_model("alba.csv", lang)
except Exception as e:
    st.error(f"Fehler beim Laden von alba.csv: {e}")
    st.stop()

criteria = (
    raw.sort_values(["Dimension", "ADM-Phases", "level_num", "Description"])
        .groupby(["Dimension", "ADM-Phases", "level_num"])
        .agg(IDs=("ID", list), Descs=("Description", list))
        .reset_index()
)

# stable sort by defined phase order then level
criteria["phase_order"] = criteria["ADM-Phases"].apply(
    lambda p: phase_order.index(p) if p in phase_order else len(phase_order))
criteria = criteria.sort_values(["phase_order", "level_num"]).reset_index(drop=True)

# restore snapshot post i18n toggle
if "__resp_snapshot" in st.session_state:
    for _, row in criteria.iterrows():
        for item_id in row["IDs"]:
            k = checkbox_key(item_id)
            if k in st.session_state["__resp_snapshot"]:
                st.session_state[k] = bool(st.session_state["__resp_snapshot"][k])
    del st.session_state["__resp_snapshot"]

id_to_value, triple_to_value = load_value_data("mehrwert.csv", lang)


def value_for_group(dim: str, phase: str, lvl: int, ids: list[str]) -> list[str]:
    key = (str(dim).strip(), core.normalize_phase(phase), int(lvl))  # noqa
    if key in triple_to_value:
        v = triple_to_value[key]
        return [v for _ in ids]
    return [id_to_value.get(str(i).strip(), "") for i in ids]


criteria["Values"] = criteria.apply(
    lambda r: value_for_group(r["Dimension"], r["ADM-Phases"], r["level_num"], r["IDs"]),
    axis=1
)

# ------------------------------
# Title & Intro
# ------------------------------
st.title(texts["title"])
st.markdown(texts["intro"])

# ------------------------------
# Sidebar actions
# ------------------------------
with st.sidebar:
    st.subheader(texts["glossary"])

    glossary, _ = core.load_glossary("glossary.csv")

    terms = sorted(glossary.keys(), key=str.casefold)
    if not terms:
        st.info("No glossary entries." if lang == "en" else "Keine Glossareinträge.")
    else:
        placeholder = "(please choose)" if lang == "en" else "(bitte wählen)"
        term = st.selectbox(
            texts["select_term"],
            options=[placeholder] + terms,
            index=0,
            key="glossary_select",
        )

        if term != placeholder:
            text = (glossary.get(term, {}).get(lang) or "").strip()
            if text:
                st.markdown(text)
            else:
                st.info(
                    "No definition available in the selected language."
                    if lang == "en"
                    else "Keine Definition in der gewählten Sprache verfügbar."
                )


with st.sidebar:
    st.subheader(texts["sidebar_tests"])
    col_a, col_b = st.columns(2)

    with col_a:
        if st.button(texts["btn_random"]):
            init_state_if_missing(criteria)
            for _, row in criteria.iterrows():
                p = fill_probability(int(row["level_num"]))
                for item_id in row["IDs"]:
                    st.session_state[checkbox_key(item_id)] = (core.random.random() < p)  # noqa
            st.rerun()

    with col_b:
        if st.button(texts["btn_reset"]):
            for k in list(st.session_state.keys()):
                if isinstance(k, str) and k.startswith(RESP_KEY_PREFIX):
                    st.session_state[k] = False
            st.rerun()

# ------------------------------
# Checklists
# ------------------------------
init_state_if_missing(criteria)
for _, row in criteria.iterrows():
    dim, phase, level = row["Dimension"], row["ADM-Phases"], row["level_num"]
    header = f"{dim} – {phase} – Level {level}" if phase else f"{dim} – Level {level}"

    with st.expander(header, expanded=False):
        first_id = row["IDs"][0] if row["IDs"] else None
        for item_id, desc, val in zip(row["IDs"], row["Descs"], row["Values"]):
            desc_str = str(desc).strip()
            if not desc_str:
                continue
            k = checkbox_key(item_id)
            if item_id == first_id:
                col1, col2 = st.columns([20, 1])
                with col1:
                    st.checkbox(desc_str, key=k)
                with col2:
                    with st.popover("ℹ️"):
                        st.markdown(f"**{texts['benefit_title']}**\n\n{value_to_bullets(val, lang)}")
            else:
                st.checkbox(desc_str, key=k)

# ------------------------------
# Evaluation, charts, exports in sidebar
# ------------------------------
responses_df = collect_responses(criteria, st.session_state)
df_res, grp_levels, x_order = summarize(responses_df)

chart = alt.Chart(df_res).transform_fold(
    fold=["Baseline", "Ceiling"], as_=["Metric", "Level"]
).mark_line(point=True).encode(
    x=alt.X("Label:N", title="Phase / Dimension", sort=x_order),
    y=alt.Y("Level:Q", title="Level"),
    color=alt.Color("Metric:N", title=texts["chart-sidebar-heading"]),
    tooltip=[alt.Tooltip("Label:N", title="Phase/Dimension"),
             alt.Tooltip("Metric:N", title=texts["chart-sidebar-heading"]),
             alt.Tooltip("Level:Q", title="Level")]
)

with st.sidebar:
    st.subheader(texts["sidebar_chart"])
    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")
    st.subheader(texts["export"])
    col_docx, col_xlsx = st.columns(2)

    # ---- DOCX ----
    with col_docx:
        if not DOCX_AVAILABLE:
            st.button(texts["btn_docx"], disabled=True, use_container_width=True)
            st.caption(texts["docx_info"])
        else:
            if st.button(texts["btn_docx"], use_container_width=True):
                try:
                    buf = build_docx_report(df_res, responses_df, lang)
                    st.session_state["__docx_bytes"] = buf.getvalue()
                except Exception as e:
                    st.error(f"Error while creating DOCX: {e}")

            if "__docx_bytes" in st.session_state:
                st.download_button(
                    label=texts["download_docx"],
                    data=st.session_state["__docx_bytes"],
                    file_name=f"eam_maturity_report_{datetime.now():%Y-%m-%d_%H-%M-%S}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )

    # ---- XLSX ----
    with col_xlsx:
        if st.button(texts["btn_xlsx"], use_container_width=True):
            try:
                buf = generate_excel_report(df_res, responses_df, lang)
                st.session_state["__xlsx_bytes"] = buf.getvalue()
            except Exception as e:
                st.error(f"Error while creating Excel: {e}")

        if "__xlsx_bytes" in st.session_state:
            st.download_button(
                label=texts["download_xlsx"],
                data=st.session_state["__xlsx_bytes"],
                file_name=f"eam_maturity_{datetime.now():%Y-%m-%d_%H-%M-%S}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

# ------------------------------
# Tables
# ------------------------------
st.subheader(texts["results"])
st.dataframe(df_res, use_container_width=True)

st.subheader(texts["next_steps"])
df_next = build_next_steps(df_res, grp_levels, responses_df)
if df_next.empty:
    st.success(texts["no_next"])
else:
    st.dataframe(df_next, use_container_width=True)
