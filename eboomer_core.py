"""Dati e logica di scoring E-Boomer Scale."""

PROFILE_KEYS = [
    "fondamentalista",
    "pentito",
    "entusiasta",
    "pragmatico",
    "occulto",
]

PROFILE_LABELS = {
    "fondamentalista": "Boomer Fondamentalista",
    "pentito": "Boomer Pentito",
    "entusiasta": "Entusiasta Digitale",
    "pragmatico": "Pragmatico Ibrido",
    "occulto": "Cyber-Neurologo Occulto",
}

QUESTIONS = [
    {
        "id": 1,
        "text": "Quando ricevi una notifica dalla cartella clinica elettronica durante la visita ambulatoriale, la tua reazione istintiva è:",
        "options": {
            "A": "Irritazione: distrae dal rapporto medico-paziente",
            "B": "Fastidio, ma riconosco che ormai fa parte del lavoro",
            "C": "Neutralità: è uno strumento come un altro",
            "D": "Soddisfazione: finalmente tutto è tracciato e accessibile",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [1, 3, 0, 1, 0],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 1],
        },
    },
    {
        "id": 2,
        "text": "Un algoritmo di IA segnala un possibile pattern epilettico su un EEG che avevi letto come normale. Tu:",
        "options": {
            "A": "Ignori l'alert: la macchina non capisce il contesto clinico",
            "B": "Rileggi con attenzione, ma resti scettico sulla validità",
            "C": "Rivaluti l'EEG integrando il suggerimento con il quadro clinico",
            "D": "Ringrazi il sistema e lo citi nel referto come supporto decisionale",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [1, 2, 0, 2, 0],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 1, 3, 1, 2],
        },
    },
    {
        "id": 3,
        "text": "Il tuo atteggiamento verso la telemedicina neurologica è:",
        "options": {
            "A": "Fondamentalmente contrario: la neurologia richiede presenza",
            "B": "Accettabile solo in emergenze o follow-up banali",
            "C": "Utile per follow-up selezionati e pazienti fragili",
            "D": "Una modalità paritaria che amplia l'accesso alle cure",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [1, 3, 0, 1, 0],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 2],
        },
    },
    {
        "id": 4,
        "text": "Prescrivi digital therapeutics (app per cefalea, riabilitazione cognitiva, ecc.)?",
        "options": {
            "A": "Mai: preferisco farmaci e terapie tradizionali",
            "B": "Raramente, e solo se il paziente insiste",
            "C": "Occasionalmente, quando c'è evidenza e il paziente è motivato",
            "D": "Regolarmente: sono parte del mio armamentario terapeutico",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [0, 3, 0, 2, 0],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 2],
        },
    },
    {
        "id": 5,
        "text": "La tua presenza sui social media professionali (LinkedIn, X, ResearchGate) è:",
        "options": {
            "A": "Inesistente e volutamente così",
            "B": "Minima: profilo creato ma quasi mai aggiornato",
            "C": "Moderata: condivisioni e aggiornamenti occasionali",
            "D": "Attiva: condivido contenuti, dibattiti e aggiornamenti",
        },
        "weights": {
            "A": [2, 0, 0, 0, 2],
            "B": [1, 2, 0, 1, 2],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 1],
        },
    },
    {
        "id": 6,
        "text": "Quando leggi un articolo su IA applicata alla neurologia, pensi:",
        "options": {
            "A": "È hype: mancano RCT e la pratica reale è diversa",
            "B": "Interessante, ma aspetto almeno un decennio prima di applicarlo",
            "C": "Promettente: seguo l'evoluzione con spirito critico",
            "D": "Entusiasmante: vorrei implementarlo nel mio setting",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [1, 3, 0, 1, 0],
            "C": [0, 0, 2, 3, 1],
            "D": [0, 0, 3, 1, 2],
        },
    },
    {
        "id": 7,
        "text": "Usi lo smartphone durante il colloquio neurologico?",
        "options": {
            "A": "Mai in ambulatorio: solo carta e penna",
            "B": "Solo per consultare farmaci o calcolatori, di nascosto",
            "C": "Per scale cliniche validate e calcolatori standardizzati",
            "D": "Per scale, note vocali, foto lesioni e accesso al referto",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [0, 1, 0, 1, 3],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 2],
        },
    },
    {
        "id": 8,
        "text": "I dati da wearable (smartwatch, EEG portatile) nel tuo lavoro:",
        "options": {
            "A": "Non li considero dati clinici validi",
            "B": "Li guardo con curiosità ma non li integro",
            "C": "Li uso se il paziente li porta e sono interpretabili",
            "D": "Li prescrivo attivamente come estensione del monitoraggio",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [1, 2, 0, 2, 0],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 2],
        },
    },
    {
        "id": 9,
        "text": "Hai mai usato ChatGPT o LLM simili per attività neurologiche?",
        "options": {
            "A": "No, e non ho intenzione di farlo",
            "B": "Ho provato per curiosità, ma non in contesto clinico",
            "C": "Occasionalmente per bozze di lettere o sintesi letteratura",
            "D": "Regolarmente per sintesi, differenziali e formazione",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [0, 2, 0, 1, 3],
            "C": [0, 0, 1, 3, 2],
            "D": [0, 0, 3, 1, 2],
        },
    },
    {
        "id": 10,
        "text": "La prenotazione online degli ambulatori neurologici:",
        "options": {
            "A": "Complica il lavoro e allontana i pazienti fragili",
            "B": "Va bene per i giovani, meno per gli anziani",
            "C": "È utile se affiancata da canali tradizionali",
            "D": "Migliora l'accesso e riduce le inefficienze",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [1, 3, 0, 1, 0],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 1],
        },
    },
    {
        "id": 11,
        "text": "Condivisione open data e dataset neurologici:",
        "options": {
            "A": "Rifiuto: rischio privacy e uso improprio",
            "B": "Solo se anonimizzazione perfetta e consenso esplicito",
            "C": "Favorevole con governance etica e infrastrutture sicure",
            "D": "Essenziale per il progresso: partecipo attivamente",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [1, 2, 0, 2, 0],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 2],
        },
    },
    {
        "id": 12,
        "text": "Un paper con co-autore IA (es. GPT) su una rivista peer-reviewed:",
        "options": {
            "A": "Inaccettabile: mina l'integrità scientifica",
            "B": "Accettabile solo in methods, mai in authorship",
            "C": "Discutibile caso per caso con trasparenza totale",
            "D": "Normale evoluzione: conta la validazione umana",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [1, 3, 0, 2, 0],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 2],
        },
    },
    {
        "id": 13,
        "text": "La realtà virtuale in riabilitazione neurologica:",
        "options": {
            "A": "Giocattolo costoso senza evidenza solida",
            "B": "Interessante in ricerca, prematuro in clinica",
            "C": "Utile in centri selezionati con protocolli definiti",
            "D": "Strumento promettente che integrerei volentieri",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [1, 2, 0, 2, 0],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 2],
        },
    },
    {
        "id": 14,
        "text": "Un algoritmo di triage assegna priorità ai tuoi pazienti in lista d'attesa. Tu:",
        "options": {
            "A": "Lo disattivi: solo il neurologo può prioritizzare",
            "B": "Lo usi come suggerimento ma decidi sempre tu",
            "C": "Lo usi se validato localmente e auditabile",
            "D": "Lo abbracci come standard per equità e efficienza",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [1, 2, 0, 2, 1],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 2],
        },
    },
    {
        "id": 15,
        "text": "Tra 10 anni, la neurologia sarà:",
        "options": {
            "A": "Sostanzialmente uguale a oggi: tecnologia marginale",
            "B": "Più digitale, ma il nucleo resterà clinico-anamnestico",
            "C": "Ibrida: IA e umano in simbiosi controllata",
            "D": "Trasformata: IA, genomica e digital health al centro",
        },
        "weights": {
            "A": [3, 0, 0, 0, 0],
            "B": [1, 3, 0, 2, 0],
            "C": [0, 0, 1, 3, 1],
            "D": [0, 0, 3, 1, 2],
        },
    },
]

PROFILES = {
    "fondamentalista": {
        "title": "Boomer Fondamentalista",
        "motto": "«Il martelletto reflexologico non ha bisogno di firmware.»",
        "description": (
            "Custode della neurologia classica, vedi la tecnologia come distrazione "
            "dal rapporto medico-paziente e dall'esame obiettivo."
        ),
        "strengths": "Osservazione clinica fine, resistenza al hype, focus sul paziente.",
        "risks": "Disallineamento con standard assistenziali digitali.",
        "prognosis": "Stabile nel breve termine; pressione formativa crescente.",
    },
    "pentito": {
        "title": "Boomer Pentito",
        "motto": "«Avevo ragione a dubitare. Ora ho ragione a imparare.»",
        "description": (
            "Hai superato lo scetticismo e stai riscoprendo il digitale con umiltà, "
            "un passo alla volta."
        ),
        "strengths": "Ponte tra scettici e innovatori, apprendimento motivato.",
        "risks": "Impostore digitale, adozione a metà di strumenti mal configurati.",
        "prognosis": "Eccellente con mentoring; evoluzione verso Pragmatico Ibrido.",
    },
    "entusiasta": {
        "title": "Entusiasta Digitale",
        "motto": "«Se non è nel cloud, non è nella mia testa.»",
        "description": (
            "Abbracci IA, telemedicina e digital therapeutics. "
            "Per te la neurologia del futuro è già arrivata."
        ),
        "strengths": "Early adopter, visione, networking scientifico digitale.",
        "risks": "Hype-driven medicine, burnout da troppi pilota.",
        "prognosis": "Leadership in comitati innovazione e ricerca traslazionale.",
    },
    "pragmatico": {
        "title": "Pragmatico Ibrido",
        "motto": "«L'EEG prima, l'algoritmo dopo.»",
        "description": (
            "Integri tecnologia e clinica con equilibrio. Adotti solo ciò che è "
            "validato e sostenibile nel tuo contesto."
        ),
        "strengths": "Evidence-based adoption, fiducia di pazienti e colleghi.",
        "risks": "Lentezza su innovazioni urgenti, doppio carico clinico-digitale.",
        "prognosis": "Profilo ottimale per setting accademici e assistenziali.",
    },
    "occulto": {
        "title": "Cyber-Neurologo Occulto",
        "motto": "«In pubblico uso la penna. In privato, il prompt.»",
        "description": (
            "In superficie tradizionale, ma sotto sperimenti IA e automazioni in silenzio."
        ),
        "strengths": "Vantaggio competitivo nascosto, efficienza personale elevata.",
        "risks": "Incoerenza percepita, questioni etiche se la pratica resta occulta.",
        "prognosis": "Rivelazione graduale consigliata; profilo prezioso come consulente.",
    },
}


def calculate_scores(answers: dict) -> dict:
    totals = {k: 0 for k in PROFILE_KEYS}
    for q in QUESTIONS:
        choice = answers.get(q["id"])
        if choice and choice in q["weights"]:
            for i, key in enumerate(PROFILE_KEYS):
                totals[key] += q["weights"][choice][i]
    return totals


def detect_occulto_pattern(answers: dict, scores: dict) -> bool:
    occulto_signals = 0
    public_traditional = 0
    occulto_q_ids = {5, 7, 9}
    trad_q_ids = {1, 3, 10}

    for q in QUESTIONS:
        choice = answers.get(q["id"])
        if not choice:
            continue
        w = q["weights"][choice]
        if w[4] >= 2:
            occulto_signals += 1
        if q["id"] in occulto_q_ids and choice in ("B", "D"):
            occulto_signals += 1
        if q["id"] in trad_q_ids and choice in ("A", "B"):
            public_traditional += 1

    return (
        occulto_signals >= 4
        and public_traditional >= 2
        and scores["occulto"] >= scores["entusiasta"]
    )


def get_winning_profile(scores: dict, answers: dict) -> str:
    if detect_occulto_pattern(answers, scores):
        adjusted = scores.copy()
        adjusted["occulto"] += 5
        return max(PROFILE_KEYS, key=lambda k: adjusted[k])
    return max(PROFILE_KEYS, key=lambda k: scores[k])
