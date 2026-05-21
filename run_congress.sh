#!/usr/bin/env bash
# Avvia E-Boomer Scale in modalità congresso (accessibile da smartphone in rete locale).
cd "$(dirname "$0")"
echo "E-Boomer Scale — modalità congresso"
echo "Schermo proiettato (Mac): http://$(python3 -c 'from congress_config import get_local_ip; print(get_local_ip())' 2>/dev/null || echo 'IP'):8501/?view=schermo"
echo "Partecipanti: scansionano il QR su quella pagina"
echo ""
exec streamlit run app.py
