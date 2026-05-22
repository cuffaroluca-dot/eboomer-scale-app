"""Core E-Boomer Scale: caricamento CSV, scoring e assegnazione profilo."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


AXIS_KEYS = ["DT", "IR", "CEO", "HOR", "RCO", "GS"]

PROFILE_KEYS = [
    "fondamentalista",
    "pentito",
    "entusiasta",
    "pragmatico",
    "cyber_occulto",
]

PROFILE_LABELS = {
    "fondamentalista": "Boomer Fondamentalista",
    "pentito": "Boomer Pentito",
    "entusiasta": "Entusiasta Digitale",
    "pragmatico": "Pragmatico Ibrido",
    "cyber_occulto": "Cyber-Neurologo Occulto",
}

PROFILE_ALIASES = {
    "occulto": "cyber_occulto",
    "cyber_occulto": "cyber_occulto",
}

PROFILE_DETAILS = {
    "fondamentalista": {
        "title": "Boomer Fondamentalista",
        "motto": "Il martelletto reflexologico non ha bisogno di firmware.",
        "description": (
            "Difende la clinica tradizionale e guarda con sospetto strumenti digitali "
            "e AI quando non riducono chiaramente rischio, tempo o incertezza."
        ),
        "strengths": "Prudenza, attenzione al rapporto medico-paziente, memoria clinica.",
        "risks": "Rischio di perdere efficienza, interoperabilita e nuovi linguaggi di cura.",
        "prognosis": "Buona se il digitale viene introdotto come supporto concreto, non come moda.",
    },
    "pentito": {
        "title": "Boomer Pentito",
        "motto": "Avevo ragione a dubitare. Ora ho ragione a imparare.",
        "description": (
            "Sta passando da una resistenza iniziale a un'adozione piu aperta, "
            "pur mantenendo bisogno di prove, esempi e contesto."
        ),
        "strengths": "Apprendimento motivato, ponte naturale tra scettici e innovatori.",
        "risks": "Adozione intermittente o dipendente da strumenti poco configurati.",
        "prognosis": "Molto buona con mentoring pratico e casi d'uso clinicamente utili.",
    },
    "entusiasta": {
        "title": "Entusiasta Digitale",
        "motto": "Datemi un buon tool e lo provo domani mattina.",
        "description": (
            "Vede in dispositivi digitali, automazione e AI un'estensione naturale "
            "della pratica clinica e scientifica."
        ),
        "strengths": "Curiosita, energia implementativa, capacita di sperimentare.",
        "risks": "Hype, sovraccarico di strumenti e sottostima dei vincoli organizzativi.",
        "prognosis": "Ottima se affiancata da metriche, audit e governance.",
    },
    "pragmatico": {
        "title": "Pragmatico Ibrido",
        "motto": "L'AI suggerisce, il medico risponde.",
        "description": (
            "Integra innovazione e supervisione umana, cercando validazione, "
            "sostenibilita e responsabilita esplicite."
        ),
        "strengths": "Equilibrio, oversight clinico, capacita di tradurre strumenti in workflow.",
        "risks": "Possibile lentezza quando l'evidenza e incompleta ma il bisogno e urgente.",
        "prognosis": "Profilo ideale per guidare implementazioni solide in contesti reali.",
    },
    "cyber_occulto": {
        "title": "Cyber-Neurologo Occulto",
        "motto": "In pubblico uso la penna. In privato, il prompt.",
        "description": (
            "Ha cultura critica e sperimenta strumenti avanzati, ma tende a farlo "
            "senza esporsi troppo o senza dichiarare pienamente il metodo."
        ),
        "strengths": "Rigore, vantaggio operativo nascosto, attenzione a dati e riproducibilita.",
        "risks": "Incoerenza percepita e zone grigie su trasparenza, governance e responsabilita.",
        "prognosis": "Prezioso se porta allo scoperto metodo, limiti e criteri di uso dell'AI.",
    },
}

PROFILES = PROFILE_DETAILS


def load_questions(path: str = "data/questions.csv") -> pd.DataFrame:
    """Carica le domande ordinate dal CSV."""
    df = pd.read_csv(Path(path), dtype=str).fillna("")
    if "order" in df.columns:
        df["order"] = pd.to_numeric(df["order"], errors="coerce").fillna(0).astype(int)
        df = df.sort_values("order")
    return df.reset_index(drop=True)


def load_scoring(path: str = "data/scoring.csv") -> pd.DataFrame:
    """Carica la matrice di scoring A-D sugli assi DT, IR, CEO, HOR, RCO, GS."""
    df = pd.read_csv(Path(path), dtype={"question_id": str, "option": str}).fillna(0)
    for axis in AXIS_KEYS:
        if axis not in df.columns:
            df[axis] = 0
        df[axis] = pd.to_numeric(df[axis], errors="coerce").fillna(0).astype(int)
    df["option"] = df["option"].astype(str).str.upper().str.strip()
    df["question_id"] = df["question_id"].astype(str).str.strip()
    return df


def load_profiles(path: str = "data/profiles.csv") -> pd.DataFrame:
    """Carica i profili descrittivi dal CSV."""
    return pd.read_csv(Path(path), dtype=str).fillna("")


def calculate_scores(answers: dict, scoring_df: pd.DataFrame | None = None) -> dict:
    """Somma gli assi DT, IR, CEO, HOR, RCO, GS per le risposte presenti.

    Le risposte mancanti o non riconosciute vengono ignorate.
    """
    if scoring_df is None:
        scoring_df = load_scoring()

    totals = {axis: 0 for axis in AXIS_KEYS}
    if not answers:
        return totals

    lookup = {}
    for _, row in scoring_df.iterrows():
        key = (str(row["question_id"]).strip(), str(row["option"]).upper().strip())
        lookup[key] = {axis: int(row[axis]) for axis in AXIS_KEYS}

    for question_id, option in answers.items():
        row_scores = lookup.get((str(question_id).strip(), str(option).upper().strip()))
        if not row_scores:
            continue
        for axis in AXIS_KEYS:
            totals[axis] += row_scores[axis]

    return totals


def assign_profile(scores: dict) -> str:
    """Assegna un profilo leggibile a partire dai sei assi di scoring."""
    s = {axis: int(scores.get(axis, 0) or 0) for axis in AXIS_KEYS}
    answered_signal = sum(s.values())
    if answered_signal == 0:
        return "pentito"

    high = 12
    medium = 7
    low = 4

    if s["RCO"] >= high and s["CEO"] >= medium and s["GS"] >= medium:
        return "cyber_occulto"

    if s["CEO"] >= high and s["HOR"] >= high and s["IR"] >= medium:
        return "pragmatico"

    if s["DT"] >= high and s["IR"] >= medium and s["HOR"] < high and s["GS"] < high:
        return "entusiasta"

    if s["DT"] <= low and s["IR"] <= low and s["RCO"] <= low:
        return "fondamentalista"

    if s["IR"] >= medium and s["DT"] >= medium and s["CEO"] >= medium:
        return "pentito"

    axis_leader = max(AXIS_KEYS, key=lambda axis: s[axis])
    if axis_leader == "HOR":
        return "pragmatico"
    if axis_leader == "RCO":
        return "cyber_occulto"
    if axis_leader in {"DT", "GS"}:
        return "entusiasta"
    if axis_leader == "CEO":
        return "pentito"
    return "fondamentalista"


def get_profile(profile_id: str, profiles_df: pd.DataFrame) -> dict:
    """Restituisce il profilo richiesto come dict.

    Prima cerca un profile_id nel CSV. Se il CSV contiene solo profili di asse
    (DT, IR, CEO, HOR, RCO, GS), usa i dettagli interni dei cinque profili finali.
    """
    normalized_id = PROFILE_ALIASES.get(profile_id, profile_id)

    if profiles_df is not None and "profile_id" in profiles_df.columns:
        matches = profiles_df[profiles_df["profile_id"] == normalized_id]
        if not matches.empty:
            return matches.iloc[0].to_dict()

    if normalized_id in PROFILE_DETAILS:
        return PROFILE_DETAILS[normalized_id].copy()

    raise KeyError(f"Profilo non trovato: {profile_id}")


def questions_as_records(questions_df: pd.DataFrame | None = None) -> list[dict]:
    """Adatta questions.csv al formato usato dalla UI Streamlit esistente."""
    if questions_df is None:
        questions_df = load_questions()

    records = []
    for _, row in questions_df.iterrows():
        records.append(
            {
                "id": row["question_id"],
                "text": row["question_text"],
                "options": {
                    "A": row["option_a"],
                    "B": row["option_b"],
                    "C": row["option_c"],
                    "D": row["option_d"],
                },
            }
        )
    return records


def get_winning_profile(scores: dict, answers: dict | None = None) -> str:
    """Compatibilita con la UI esistente."""
    return assign_profile(scores)


QUESTIONS = questions_as_records()
