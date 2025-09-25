"""
core.py
Data loading, normalization, state helpers, and maturity calculations.
"""

from typing import Dict, Tuple, List
import re
import pandas as pd
from config import LEVEL_FILL_PROB, phase_order, RESP_KEY_PREFIX


# ---------- Loading & normalization ----------

def load_model(alba_path: str, lang: str) -> pd.DataFrame:
    """
    Load and normalize the model source from `alba.csv`.

    Expected columns:
        - Dimension; ADM-Phases; Maturity Level; ID; Description_EN; Description_DE

    Args:
        alba_path: CSV path.
        lang: "en" or "de" – selects preferred language, with fallback to the other.

    Returns:
        DataFrame with columns:
            ["Dimension", "ADM-Phases", "level_num", "ID", "Description"]
        - level_num is an integer extracted from "Maturity Level".
        - Description is chosen by language with fallback.
        - Rows with level <= 0 or empty descriptions are removed.

    Raises:
        ValueError: if required columns are missing.
    """
    df = pd.read_csv(alba_path, sep=";", encoding="utf-8-sig")
    required = {"Dimension", "ADM-Phases", "Maturity Level", "ID", "Description_EN", "Description_DE"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"alba.csv missing: {', '.join(sorted(missing))}")

    df["Dimension"] = df["Dimension"].ffill()
    df["ADM-Phases"] = df.groupby("Dimension")["ADM-Phases"].ffill().fillna("")
    df["level_num"] = df["Maturity Level"].str.extract(r"(\d+)").astype("Int64")
    df["ID"] = df["ID"].astype(str)

    def pick_desc(row):
        de = str(row.get("Description_DE", "") or "").strip()
        en = str(row.get("Description_EN", "") or "").strip()
        return de if lang == "de" and de else (en if en else de)

    df["Description"] = df.apply(pick_desc, axis=1)
    df = df[(df["level_num"] > 0) & (df["Description"].astype(str).str.strip() != "")]
    return df[["Dimension", "ADM-Phases", "level_num", "ID", "Description"]]


def normalize_phase(p) -> str:
    """
    Normalize ADM phase labels.

    - Maps ARM to empty string (cross-cutting, no phase).
    - Collapses the combined B/C/D phase to a single canonical text.
    - Returns "" for placeholders like "-", "–", "—" or empty.

    Args:
        p: Phase value (any type).

    Returns:
        Canonical string for the phase.
    """
    if p is None or (pd.isna(p)):
        return ""
    s = str(p).strip()
    if s in ("", "-", "–", "—"):
        return ""
    low = s.lower()
    if low.startswith(("architecture requirements management", "requirements management", "arm")):
        return ""
    if "business, information systems and technology architecture" in low:
        return "B, C, D – Business, Information Systems and Technology Architecture"
    if s == "D – Business, Information Systems and Technology Architecture":
        return "B, C, D – Business, Information Systems and Technology Architecture"
    return s


def load_value_data(path: str, lang: str) -> Tuple[Dict[str, str], Dict[Tuple[str, str, int], str]]:
    """
    Load “benefit/value” text from `mehrwert.csv`.

    Supported shapes:
        (A) ID-based:
            - ID, Value_EN/Value_DE (optional Dimension/Phase/Level for cross-check)
        (B) Triple-based:
            - Dimension; ADM-Phases; Maturity Level; Value_EN/Value_DE

    Args:
        path: CSV path.
        lang: "en" or "de" – selects value column (fallback to any *value/mehrwert* if needed).

    Returns:
        (id_to_value, triple_to_value)
            - id_to_value: maps ID -> text
            - triple_to_value: maps (Dimension, normalized Phase, level_num) -> text
        Empty dicts are returned if the file is missing or no suitable columns are found.
    """
    try:
        vdf = pd.read_csv(path, sep=";", encoding="utf-8-sig", keep_default_na=False)
    except FileNotFoundError:
        return {}, {}

    colmap = {c.lower(): c for c in vdf.columns}
    def has(name: str) -> bool: return name in colmap

    candidates_de = ["value_de", "mehrwert", "mehrwert_de", "value"]
    candidates_en = ["value_en", "mehrwert_en", "value"]
    value_col_lc = next((c for c in (candidates_de if lang == "de" else candidates_en) if has(c)), None)
    if not value_col_lc:
        value_col_lc = next((c for c in colmap if "value" in c or "mehrwert" in c), None)
    if not value_col_lc:
        return {}, {}
    value_col = colmap[value_col_lc]

    id_to_value: Dict[str, str] = {}
    triple_to_value: Dict[Tuple[str, str, int], str] = {}

    if has("id"):
        idcol = colmap["id"]
        tmp = vdf[[idcol, value_col]].copy()
        tmp[idcol] = tmp[idcol].astype(str).str.strip()
        tmp[value_col] = tmp[value_col].astype(str).fillna("").str.strip()
        id_to_value = dict(zip(tmp[idcol], tmp[value_col]))

        if has("dimension") and has("adm-phases") and has("maturity level"):
            dcol, pcol, lcol = colmap["dimension"], colmap["adm-phases"], colmap["maturity level"]
            tmp2 = vdf[[dcol, pcol, lcol, value_col]].copy()
            tmp2[dcol] = tmp2[dcol].astype(str).str.strip()
            tmp2[pcol] = tmp2[pcol].map(normalize_phase)
            tmp2["level_num"] = tmp2[lcol].astype(str).str.extract(r"(\d+)").astype(int)
            tmp2[value_col] = tmp2[value_col].astype(str).fillna("").str.strip()
            for _, r in tmp2.iterrows():
                triple_to_value[(r[dcol], r[pcol], int(r["level_num"]))] = r[value_col]
        return id_to_value, triple_to_value

    if has("dimension") and has("adm-phases") and has("maturity level"):
        dcol, pcol, lcol = colmap["dimension"], colmap["adm-phases"], colmap["maturity level"]
        tmp = vdf[[dcol, pcol, lcol, value_col]].copy()
        tmp[dcol] = tmp[dcol].astype(str).str.strip()
        tmp[pcol] = tmp[pcol].map(normalize_phase)
        tmp["level_num"] = tmp[lcol].astype(str).str.extract(r"(\d+)").astype(int)
        tmp[value_col] = tmp[value_col].astype(str).fillna("").str.strip()
        for _, r in tmp.iterrows():
            triple_to_value[(r[dcol], r[pcol], int(r["level_num"]))] = r[value_col]
        return {}, triple_to_value

    return {}, {}


# ---------- Display helpers & state ----------

DASH_CHARS = r"\-\u2013\u2014\u2212"

def value_to_bullets(val, lang: str) -> str:
    """
    Convert a dash-separated string into a Markdown bullet list.

    Splits only on ' SPACE + dash + SPACE ' to avoid breaking words like “ad-hoc”.

    Args:
        val: Raw text.
        lang: "en" or "de" – used for empty-text fallback.

    Returns:
        Markdown string with bullet lines.
    """
    s = "" if val is None else str(val).strip()
    if not s:
        return "Mehrwert nicht verfügbar." if lang == "de" else "Value not available."
    s = re.sub(rf"^\s*[{DASH_CHARS}]\s*", "", s)
    parts = [p.strip(" .;,") for p in re.split(rf"\s[{DASH_CHARS}]\s+", s) if p.strip()]
    parts = parts or [s]
    return "\n".join(f"- {p}" for p in parts)


def fill_probability(level: int) -> float:
    """
    Probability to mark a criterion as fulfilled when “random fill” is used.

    Args:
        level: Maturity level (int).

    Returns:
        Probability in [0, 1].
    """
    return LEVEL_FILL_PROB.get(int(level), 0.50)


def checkbox_key(item_id: str) -> str:
    """
    Build a stable Streamlit session_state key for a criterion ID.

    Args:
        item_id: Criterion ID from `alba.csv`.

    Returns:
        Key string, e.g. "resp|42".
    """
    return f"{RESP_KEY_PREFIX}{item_id}"


def init_state_if_missing(criteria: pd.DataFrame) -> None:
    """
    Ensure all checkbox keys exist in Streamlit session_state, initialized to False.

    Args:
        criteria: Grouped criteria DataFrame containing an "IDs" list column.
    """
    import streamlit as st
    for _, row in criteria.iterrows():
        for item_id in row["IDs"]:
            k = checkbox_key(item_id)
            if k not in st.session_state:
                st.session_state[k] = False


def collect_responses(criteria: pd.DataFrame, session_state) -> pd.DataFrame:
    """
    Flatten UI state into a row-per-criterion DataFrame.

    Args:
        criteria: Grouped criteria DataFrame with columns ["Dimension","ADM-Phases","level_num","IDs","Descs"].
        session_state: Streamlit session_state (dict-like) holding checkbox values.

    Returns:
        DataFrame with columns:
            ["ID","Dimension","ADM-Phases","level_num","Description","Checked"].
    """
    records = []
    for _, row in criteria.iterrows():
        for item_id, desc in zip(row["IDs"], row["Descs"]):
            records.append({
                "ID": item_id,
                "Dimension": row["Dimension"],
                "ADM-Phases": row["ADM-Phases"],
                "level_num": row["level_num"],
                "Description": desc,
                "Checked": bool(session_state.get(checkbox_key(item_id), False)),
            })
    return pd.DataFrame(records)


# ---------- Maturity calculations ----------

def summarize(responses_df: pd.DataFrame):
    """
    Compute Baseline/Ceiling per (Dimension, Phase) and a sorted summary table.

    Baseline rule:
        Highest level k such that *all* criteria up to and including k are fulfilled.
    Ceiling rule:
        Highest level with *any* fulfilled criterion (0 if none).

    Args:
        responses_df: Output of `collect_responses`.

    Returns:
        (df_res, grp_levels, x_order)
            - df_res: summary per (Dimension, Phase) with columns
              ["Dimension","ADM-Phases","Baseline","Ceiling","Label","Average"]
            - grp_levels: per (Dimension, Phase, Level) counts (internal use)
            - x_order: stable order of labels for charts
    """
    grp = (responses_df.groupby(["Dimension", "ADM-Phases", "level_num"])
           .agg(total=("Checked", "count"), done=("Checked", "sum"))
           .reset_index())
    grp["fulfilled"] = grp["done"] == grp["total"]
    grp["any"] = grp["done"] > 0

    results = []
    for (dim, phase), sub in grp.groupby(["Dimension", "ADM-Phases"], sort=False):
        baseline = 0
        for k in sorted(sub["level_num"].unique()):
            if sub.loc[sub["level_num"] <= k, "fulfilled"].all():
                baseline = k
        ceiling = sub.loc[sub["any"], "level_num"].max() if sub["any"].any() else 0
        results.append({"Dimension": dim, "ADM-Phases": phase, "Baseline": baseline, "Ceiling": ceiling})

    df_res = pd.DataFrame(results)
    df_res["Label"] = df_res.apply(lambda r: r["ADM-Phases"] if r["ADM-Phases"] else r["Dimension"], axis=1)

    def _phase_rank(ph): return phase_order.index(ph) if ph in phase_order else len(phase_order)
    df_res["__rank"] = df_res["ADM-Phases"].apply(_phase_rank)
    df_res = df_res.sort_values(["__rank", "Label"]).drop(columns="__rank").reset_index(drop=True)

    df_res["Average"] = (df_res["Baseline"] + df_res["Ceiling"]) / 2
    x_order = df_res["Label"].tolist()
    return df_res, grp, x_order


def build_next_steps(df_res: pd.DataFrame, grp_levels: pd.DataFrame, responses_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a “next steps” list for each (Dimension, Phase).

    For each summary row, target the immediate next level:
        target = max(1, Baseline + 1)  (or 1 if Ceiling == 0)
    Then list all unchecked criteria at that target level.

    Args:
        df_res: Summary from `summarize`.
        grp_levels: Level aggregation from `summarize` (not used for logic but kept for compatibility).
        responses_df: Row-per-criterion dataframe from `collect_responses`.

    Returns:
        DataFrame with columns ["Dimension","ADM-Phases","Level","ToDo"], sorted for display.
    """
    next_rows: List[Dict[str, str]] = []
    for _, r in df_res.iterrows():
        dim, phase = r["Dimension"], r["ADM-Phases"]
        baseline, ceiling = int(r["Baseline"]), int(r["Ceiling"])

        target_level = 1 if ceiling == 0 else max(1, baseline + 1)

        crits = responses_df[
            (responses_df["Dimension"] == dim) &
            (responses_df["ADM-Phases"] == phase) &
            (responses_df["level_num"] == target_level)
            ]
        if crits.empty:
            continue

        for _, row in crits[~crits["Checked"]].iterrows():
            next_rows.append({
                "Dimension": dim,
                "ADM-Phases": phase if phase else "(no phase)",
                "Level": target_level,
                "ToDo": row["Description"],
            })

    return pd.DataFrame(next_rows).sort_values(["Dimension", "ADM-Phases", "Level"]).reset_index(drop=True)
