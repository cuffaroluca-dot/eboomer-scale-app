"""Schermo congresso: QR code e risultati live."""

import io

import qrcode
import streamlit as st

from congress_config import (
    get_base_url,
    get_event_id,
    get_local_ip,
    get_professor_ids,
    participant_url,
    set_event_id,
    set_professor_ids,
    set_public_url,
)
from eboomer_core import PROFILE_KEYS, PROFILE_LABELS, PROFILES
from storage import get_aggregate, get_source_totals, reset_event
from ui_styles import BASE_CSS, PRESENTER_CSS


def make_qr_image(url: str) -> bytes:
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def render_presenter_screen() -> None:
    st.markdown(BASE_CSS + PRESENTER_CSS, unsafe_allow_html=True)
    st.markdown('<meta http-equiv="refresh" content="5">', unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Setup congresso")
        st.caption("Configura prima di proiettare.")

        event_input = st.text_input("ID sessione", value=get_event_id())
        if st.button("Applica ID sessione"):
            set_event_id(event_input)
            st.rerun()

        st.divider()
        st.caption(f"IP su questa rete: **{get_local_ip()}**")

        url_input = st.text_input("URL pubblico (opzionale)", value=get_base_url())
        if st.button("Salva URL"):
            set_public_url(url_input)
            st.rerun()

        st.divider()
        st.markdown("**Schermo proiettato (questo Mac):**")
        st.code("?view=schermo", language=None)
        st.markdown("**Smartphone (QR):**")
        st.code(participant_url(), language=None)

        st.divider()
        st.markdown("**ID professori**")
        professor_ids = get_professor_ids()
        edited_ids = []
        for idx, professor_id in enumerate(professor_ids, start=1):
            edited_ids.append(
                st.text_input(f"Professore {idx}", value=professor_id, key=f"prof_id_{idx}")
            )
        if st.button("Salva ID professori"):
            set_professor_ids(edited_ids)
            st.rerun()

        st.divider()
        if st.button("🗑️ Azzera risposte sessione", type="secondary"):
            n = reset_event(get_event_id())
            st.success(f"Eliminate {n} risposte.")
            st.rerun()

        st.checkbox("Aggiornamento automatico (5 s)", value=True, disabled=True)
        if st.button("🔄 Aggiorna ora"):
            st.rerun()

    event_id = get_event_id()
    join_url = participant_url()
    professor_ids = get_professor_ids()
    agg = get_aggregate(event_id)
    source_totals = get_source_totals(event_id)
    total = agg["total"]
    counts = agg["counts"]

    st.markdown('<div class="presenter-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="presenter-h1">E-Boomer Scale</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="presenter-h2">Scansiona il QR · rispondi dal telefono · guarda i risultati qui</p>',
        unsafe_allow_html=True,
    )

    col_qr, col_instr = st.columns([1, 1.2])

    with col_qr:
        st.image(make_qr_image(join_url), width=320, caption="Inquadra con la fotocamera")
        st.markdown(
            f'<p style="text-align:center;font-family:Inter,sans-serif;font-size:0.85rem;'
            f'color:#64748b;word-break:break-all;">{join_url}</p>',
            unsafe_allow_html=True,
        )

    with col_instr:
        st.markdown(
            """
            <div class="presenter-instructions">
            <strong>Come partecipare</strong><br><br>
            1. Stesso Wi‑Fi del congresso<br>
            2. Inquadra il QR con la fotocamera<br>
            3. Compila le 15 domande (~3 min)<br>
            4. Il profilo appare sul telefono<br>
            5. I risultati della platea si aggiornano qui
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("QR professori personalizzati"):
        st.caption(
            "Ogni QR entra nella stessa sessione ma registra un ID sorgente diverso."
        )
        prof_cols = st.columns(5)
        for idx, professor_id in enumerate(professor_ids):
            url = participant_url(source_id=professor_id)
            with prof_cols[idx % 5]:
                st.image(make_qr_image(url), width=135, caption=professor_id)
                st.caption(f"{source_totals.get(professor_id, 0)} risposte")

    st.divider()

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<p class="presenter-stat">{total}</p>', unsafe_allow_html=True)
        st.markdown('<p class="presenter-stat-label">Risposte ricevute</p>', unsafe_allow_html=True)
    with m2:
        leader = max(PROFILE_KEYS, key=lambda k: counts[k]) if total else None
        leader_name = PROFILE_LABELS[leader] if leader else "—"
        st.markdown(
            f'<p class="presenter-stat" style="font-size:1.5rem;">{leader_name}</p>',
            unsafe_allow_html=True,
        )
        st.markdown('<p class="presenter-stat-label">Profilo più frequente</p>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<p class="presenter-stat">{event_id}</p>', unsafe_allow_html=True)
        st.markdown('<p class="presenter-stat-label">Sessione attiva</p>', unsafe_allow_html=True)

    st.subheader("Distribuzione della platea")

    if total == 0:
        st.info("In attesa delle prime risposte… Mostra il QR e invita il pubblico.")
    else:
        chart_data = {PROFILE_LABELS[k]: counts[k] for k in PROFILE_KEYS}
        st.bar_chart(chart_data)

        cols = st.columns(len(PROFILE_KEYS))
        for col, key in zip(cols, PROFILE_KEYS):
            pct = round(100 * counts[key] / total)
            with col:
                st.metric(PROFILE_LABELS[key], counts[key], f"{pct}%", delta_color="off")

        if total >= 3:
            top_key = max(PROFILE_KEYS, key=lambda k: counts[k])
            top = PROFILES[top_key]
            st.markdown("---")
            st.markdown(f"### Profilo dominante: **{top['title']}**")
            st.markdown(f"*{top['motto']}*")
            st.write(top["description"])

    st.markdown("</div>", unsafe_allow_html=True)
