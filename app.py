"""
E-Boomer Scale — Partecipazione da smartphone (QR congresso).
Schermo proiettato: ?view=schermo
"""

import uuid

import streamlit as st

from congress_config import get_event_id
from eboomer_core import (
    PROFILES,
    PROFILE_KEYS,
    PROFILE_LABELS,
    QUESTIONS,
    calculate_scores,
    get_winning_profile,
)
from storage import has_submitted, save_submission
from ui_styles import BASE_CSS

_IS_PRESENTER = st.query_params.get("view") == "schermo"

st.set_page_config(
    page_title="E-Boomer Scale" + (" — Schermo Congresso" if _IS_PRESENTER else ""),
    page_icon="📊" if _IS_PRESENTER else "🧠",
    layout="wide" if _IS_PRESENTER else "centered",
    initial_sidebar_state="expanded" if _IS_PRESENTER else "collapsed",
)

if _IS_PRESENTER:
    from presenter_screen import render_presenter_screen

    render_presenter_screen()
    st.stop()

st.markdown(BASE_CSS, unsafe_allow_html=True)


def get_event_from_url() -> str:
    qp = st.query_params.get("event")
    if qp:
        return qp
    return get_event_id()


def get_source_from_url() -> str:
    qp = st.query_params.get("source")
    if qp:
        return qp.strip() or "audience"
    return "audience"


def init_session_state():
    if "step" not in st.session_state:
        st.session_state.step = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "completed" not in st.session_state:
        st.session_state.completed = False
    if "participant_id" not in st.session_state:
        st.session_state.participant_id = uuid.uuid4().hex[:12]
    if "saved_to_congress" not in st.session_state:
        st.session_state.saved_to_congress = False


def reset_assessment():
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.completed = False
    st.session_state.saved_to_congress = False


def persist_result(profile_key: str, scores: dict, event_id: str, source_id: str) -> None:
    if st.session_state.saved_to_congress:
        return
    pid = st.session_state.participant_id
    if has_submitted(pid, event_id):
        st.session_state.saved_to_congress = True
        return
    save_submission(pid, event_id, source_id, profile_key, scores)
    st.session_state.saved_to_congress = True


def render_header():
    st.markdown('<p class="eb-title">E-Boomer Scale</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="eb-subtitle">15 domande · medicina digitale, IA e tecnologia in neurologia</p>',
        unsafe_allow_html=True,
    )


def render_question(idx: int):
    q = QUESTIONS[idx]
    st.markdown(
        f'<p class="eb-meta">Domanda {idx + 1} di {len(QUESTIONS)}</p>',
        unsafe_allow_html=True,
    )
    progress = (idx + 1) / len(QUESTIONS)
    st.progress(progress, text=f"{int(progress * 100)}%")

    st.markdown(f'<p class="eb-question">{q["text"]}</p>', unsafe_allow_html=True)

    labels = [f"{k}. {v}" for k, v in q["options"].items()]
    keys = list(q["options"].keys())
    current = st.session_state.answers.get(q["id"])
    default_idx = keys.index(current) if current in keys else None

    choice_label = st.radio(
        "Risposta",
        options=labels,
        index=default_idx,
        key=f"radio_q{q['id']}",
        label_visibility="collapsed",
    )
    st.session_state.answers[q["id"]] = keys[labels.index(choice_label)]


def render_results(event_id: str, source_id: str):
    scores = calculate_scores(st.session_state.answers)
    profile_key = get_winning_profile(scores, st.session_state.answers)
    profile = PROFILES[profile_key]
    persist_result(profile_key, scores, event_id, source_id)

    st.markdown(
        '<div class="eb-banner">✓ Risposta registrata · tra poco i risultati della sala appariranno sullo schermo</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="eb-result-card">
            <p class="eb-meta">Il tuo profilo</p>
            <p class="eb-profile-title">{profile["title"]}</p>
            <p class="eb-motto">{profile["motto"]}</p>
            <p style="font-family:Inter,sans-serif;font-size:0.9rem;color:#334155;line-height:1.6;">
                {profile["description"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Dettaglio completo"):
        for label, key in [
            ("Punti di forza", "strengths"),
            ("Rischi", "risks"),
            ("Prognosi", "prognosis"),
        ]:
            st.markdown(f"**{label}**")
            st.write(profile[key])

        st.markdown("**Punteggi per profilo**")
        max_score = max(scores.values()) or 1
        for key in PROFILE_KEYS:
            st.progress(
                scores[key] / max_score,
                text=f"{PROFILE_LABELS[key]}: {scores[key]} pt",
            )


def render_navigation():
    col_prev, col_next, col_restart = st.columns([1, 1, 1])

    with col_prev:
        if st.session_state.step > 0 and not st.session_state.completed:
            if st.button("← Indietro", use_container_width=True):
                st.session_state.step -= 1
                st.rerun()

    with col_next:
        if not st.session_state.completed:
            idx = st.session_state.step
            q = QUESTIONS[idx]
            answered = q["id"] in st.session_state.answers
            label = "Avanti →" if idx < len(QUESTIONS) - 1 else "Invia risposte"
            if st.button(label, use_container_width=True, type="primary", disabled=not answered):
                if idx < len(QUESTIONS) - 1:
                    st.session_state.step += 1
                else:
                    st.session_state.completed = True
                st.rerun()

    with col_restart:
        if st.button("↺ Ricomincia", use_container_width=True):
            reset_assessment()
            st.rerun()


def main():
    init_session_state()
    event_id = get_event_from_url()
    source_id = get_source_from_url()

    render_header()
    st.caption(f"Sessione: **{event_id}** · anonimo")

    if st.session_state.completed:
        render_results(event_id, source_id)
    else:
        st.info("Compila tutte le domande dal telefono. Ci vogliono circa 3 minuti.")
        render_question(st.session_state.step)

    st.markdown('<hr class="eb-divider">', unsafe_allow_html=True)
    render_navigation()

    if not st.session_state.completed:
        st.caption("Strumento satirico-educativo per contesti congressuali.")


if __name__ == "__main__":
    main()
