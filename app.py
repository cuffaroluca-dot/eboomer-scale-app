"""Streamlit app per E-Boomer Scale."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from eboomer_core import (
    AXIS_KEYS,
    calculate_scores,
    assign_profile,
    get_profile,
    load_profiles,
    load_questions,
    load_scoring,
)
from storage import get_responses_df, reset_responses, save_response
from ui_styles import BASE_CSS


SECTION_LABELS = {
    "icebreaker_digitale": "Blocco 1 — Icebreaker digitale",
    "digital_devices_ai_clinica": "Blocco 2 — Digital devices e AI clinica",
    "ai_ricerca_scienza": "Blocco 3 — AI, ricerca, scienza",
}

OPTION_KEYS = ["A", "B", "C", "D"]


st.set_page_config(
    page_title="E-Boomer Scale",
    page_icon="🧠",
    layout="wide" if st.query_params.get("admin") == "true" else "centered",
    initial_sidebar_state="collapsed",
)
st.markdown(BASE_CSS, unsafe_allow_html=True)


def query_param(name: str, default: str = "") -> str:
    value = st.query_params.get(name, default)
    if isinstance(value, list):
        return value[0] if value else default
    return value or default


def get_session_id() -> str:
    return query_param("session", query_param("event", "congresso")).strip() or "congresso"


def get_group() -> str:
    group = query_param("group", "audience").strip().lower()
    return group if group in {"audience", "faculty"} else "audience"


def get_participant_id(group: str, session_id: str) -> str:
    param_id = query_param("id", "").strip()
    if group == "faculty" and param_id:
        return param_id
    if param_id:
        return param_id
    return session_id if group == "audience" else ""


@st.cache_data
def cached_questions() -> pd.DataFrame:
    return load_questions()


@st.cache_data
def cached_scoring() -> pd.DataFrame:
    return load_scoring()


@st.cache_data
def cached_profiles() -> pd.DataFrame:
    return load_profiles()


@st.cache_data
def cached_participants() -> pd.DataFrame:
    return pd.read_csv("data/participants.csv", dtype=str).fillna("")


def get_display_name(participant_id: str, group: str, participants_df: pd.DataFrame) -> str:
    if group != "faculty" or not participant_id:
        return ""
    matches = participants_df[participants_df["participant_id"] == participant_id]
    if matches.empty:
        return participant_id
    display_name = matches.iloc[0].get("display_name", "").strip()
    return display_name or participant_id


def render_title() -> None:
    st.markdown('<p class="eb-title">E-Boomer Scale</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="eb-subtitle">Fenotipi neuro-digitali della neurologia contemporanea</p>',
        unsafe_allow_html=True,
    )


def option_label(row: pd.Series, option: str) -> str:
    return f"{option}. {row[f'option_{option.lower()}']}"


def render_questionnaire() -> None:
    session_id = get_session_id()
    group = get_group()
    participant_id = get_participant_id(group, session_id)
    questions_df = cached_questions()
    scoring_df = cached_scoring()
    profiles_df = cached_profiles()
    participants_df = cached_participants()
    display_name = get_display_name(participant_id, group, participants_df)

    render_title()
    st.caption(f"Sessione: **{session_id}** · gruppo: **{group}**")

    if "submitted" not in st.session_state:
        st.session_state["submitted"] = False

    if st.session_state["submitted"]:
        render_final_profile(
            st.session_state["last_profile"],
            st.session_state["last_scores"],
            group,
            display_name,
        )
        return

    with st.form("eboomer_questionnaire"):
        answers = {}
        for block, block_df in questions_df.groupby("block", sort=False):
            st.markdown(f"### {SECTION_LABELS.get(block, block)}")
            for _, row in block_df.sort_values("order").iterrows():
                question_id = row["question_id"]
                st.markdown(f"**{question_id}. {row['question_text']}**")
                labels = [option_label(row, option) for option in OPTION_KEYS]
                selected_label = st.radio(
                    "Risposta",
                    labels,
                    index=None,
                    key=f"answer_{question_id}",
                    label_visibility="collapsed",
                )
                if selected_label:
                    answers[question_id] = selected_label.split(".", 1)[0]
                if row.get("scientific_note"):
                    st.caption(row["scientific_note"])
                st.markdown("")

        submitted = st.form_submit_button("Invia risposte", type="primary", use_container_width=True)

    if not submitted:
        return

    missing = [qid for qid in questions_df["question_id"] if qid not in answers]
    if missing:
        st.warning("Completa tutte le domande prima di inviare.")
        return

    scores = calculate_scores(answers, scoring_df)
    profile_id = assign_profile(scores)
    profile = get_profile(profile_id, profiles_df)

    response = {
        "session_id": session_id,
        "group": group,
        "participant_id": participant_id,
        "display_name": display_name,
        "profile_id": profile_id,
        "profile_name": profile["profile_name"],
        **answers,
        **scores,
    }
    save_response(response)

    st.session_state["submitted"] = True
    st.session_state["last_scores"] = scores
    st.session_state["last_profile"] = profile
    st.rerun()


def render_final_profile(profile: dict, scores: dict, group: str, display_name: str) -> None:
    st.success("Risposta registrata.")
    if group == "faculty" and display_name:
        st.markdown(f"### Grazie, {display_name}")
    st.markdown(
        f"""
        <div class="eb-result-card">
            <p class="eb-meta">Il tuo fenotipo</p>
            <p class="eb-profile-title">{profile["profile_name"]}</p>
            <p class="eb-motto">{profile["motto"]}</p>
            <p style="font-family:Inter,sans-serif;font-size:0.95rem;color:#334155;line-height:1.6;">
                {profile["short_description"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Dettaglio profilo"):
        st.markdown("**Punto di forza**")
        st.write(profile["strength"])
        st.markdown("**Rischio**")
        st.write(profile["risk"])
        st.markdown("**Prognosi**")
        st.write(profile["prognosis"])
        st.markdown("**Punteggi asse**")
        max_score = max(scores.values()) or 1
        for axis in AXIS_KEYS:
            st.progress(scores[axis] / max_score, text=f"{axis}: {scores[axis]} pt")


def profile_distribution(df: pd.DataFrame, title: str) -> None:
    st.markdown(f"#### {title}")
    if df.empty:
        st.info("Nessuna risposta disponibile.")
        return
    counts = df["profile_name"].value_counts().sort_index()
    st.bar_chart(counts)


def question_distribution(df: pd.DataFrame, question_id: str) -> pd.Series:
    counts = df[question_id].value_counts().reindex(OPTION_KEYS, fill_value=0)
    counts.name = question_id
    return counts


def normalize_numeric_axes(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    for axis in AXIS_KEYS:
        if axis not in normalized.columns:
            normalized[axis] = 0
        normalized[axis] = pd.to_numeric(normalized[axis], errors="coerce").fillna(0)
    return normalized


def stretch_button(label: str, **kwargs) -> bool:
    try:
        return st.button(label, width="stretch", **kwargs)
    except TypeError:
        return st.button(label, use_container_width=True, **kwargs)


def stretch_download_button(label: str, **kwargs) -> bool:
    try:
        return st.download_button(label, width="stretch", **kwargs)
    except TypeError:
        return st.download_button(label, use_container_width=True, **kwargs)


def stretch_dataframe(data, **kwargs) -> None:
    try:
        st.dataframe(data, width="stretch", **kwargs)
    except TypeError:
        st.dataframe(data, use_container_width=True, **kwargs)


def build_faculty_table(responses_df: pd.DataFrame) -> pd.DataFrame:
    participants_df = cached_participants()
    faculty_base = participants_df[participants_df["group"] == "faculty"].copy()
    if faculty_base.empty:
        empty_table = pd.DataFrame(
            columns=[
                "display_name",
                "participant_id",
                "completed",
                "profile_name",
                *AXIS_KEYS,
            ]
        )
        return normalize_numeric_axes(empty_table)

    if responses_df.empty:
        latest_responses = pd.DataFrame(columns=["participant_id", "profile_name", *AXIS_KEYS])
    else:
        faculty_responses = responses_df[responses_df["group"] == "faculty"].copy()
        if faculty_responses.empty:
            latest_responses = pd.DataFrame(columns=["participant_id", "profile_name", *AXIS_KEYS])
        else:
            faculty_responses = faculty_responses.sort_values("timestamp")
            latest_responses = faculty_responses.drop_duplicates("participant_id", keep="last")
            latest_responses = latest_responses[["participant_id", "profile_name", *AXIS_KEYS]]
            latest_responses = normalize_numeric_axes(latest_responses)

    table = faculty_base[["participant_id", "display_name"]].merge(
        latest_responses,
        on="participant_id",
        how="left",
    )
    table["completed"] = table["profile_name"].notna()
    table["profile_name"] = table["profile_name"].fillna("")
    table = normalize_numeric_axes(table)
    return table[["display_name", "participant_id", "completed", "profile_name", *AXIS_KEYS]]


def render_admin_dashboard() -> None:
    st.title("Dashboard moderatori")
    st.caption("E-Boomer Scale · risultati live")

    col_refresh, col_download = st.columns([1, 2])
    with col_refresh:
        if stretch_button("Refresh"):
            st.rerun()

    df = normalize_numeric_axes(get_responses_df())
    audience_df = df[df["group"] == "audience"] if not df.empty else df
    faculty_df = df[df["group"] == "faculty"] if not df.empty else df

    with col_download:
        stretch_download_button(
            "Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="eboomer_responses.csv",
            mime="text/csv",
            disabled=df.empty,
        )

    m1, m2, m3 = st.columns(3)
    m1.metric("Totale risposte", len(df))
    m2.metric("Audience", len(audience_df))
    m3.metric("Faculty", len(faculty_df))

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        profile_distribution(df, "Distribuzione profili complessiva")
    with c2:
        profile_distribution(audience_df, "Distribuzione profili audience")
    with c3:
        profile_distribution(faculty_df, "Distribuzione profili faculty")

    st.divider()
    st.subheader("Faculty")
    faculty_table = build_faculty_table(df)
    stretch_dataframe(
        faculty_table.sort_values("participant_id"),
        hide_index=True,
    )

    st.divider()
    st.subheader("Risultati per domanda")
    if df.empty:
        st.info("Nessuna risposta disponibile.")
    else:
        question_counts = pd.DataFrame(
            [question_distribution(df, f"Q{i}") for i in range(1, 15)]
        )
        question_counts.index = [f"Q{i}" for i in range(1, 15)]
        question_counts = question_counts.apply(pd.to_numeric, errors="coerce").fillna(0)
        stretch_dataframe(question_counts)

        for question_id in question_counts.index:
            with st.expander(question_id):
                st.bar_chart(question_counts.loc[question_id])

    st.divider()
    st.subheader("Reset risposte")
    confirmation = st.text_input("Scrivi RESET per cancellare tutte le risposte")
    if st.button("Reset risposte", type="secondary", disabled=confirmation != "RESET"):
        deleted = reset_responses()
        st.success(f"Eliminate {deleted} risposte.")
        st.rerun()


def main() -> None:
    if query_param("admin", "").strip().lower() == "true":
        render_admin_dashboard()
    else:
        render_questionnaire()


if __name__ == "__main__":
    main()
