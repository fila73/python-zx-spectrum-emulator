#!/bin/bash

# Adresář projektu
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Vytvoření složky pro logy, pokud neexistuje
mkdir -p agent_logs

# Saturnin: Pro použití OAuth (Vaší identity) v Gemini CLI nesmí být nastaveno GEMINI_API_KEY.
# Pokud je tato proměnná prázdná nebo neexistuje, CLI automaticky použije uložený OAuth profil.
unset GEMINI_API_KEY

# Aktivace virtuálního prostředí
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "--- Saturninův agent (OAuth) startuje ---"

while true; do
    COMMIT=$(git rev-parse --short=6 HEAD 2>/dev/null || echo "init")
    LOGFILE="agent_logs/agent_${COMMIT}_$(date +%s).log"

    echo "[$(date +%T)] Běží krok agenta skrze OAuth..."
    
    # Spuštění gemini s modelem gemini-3-flash-preview bez explicitního API klíče
    gemini --yolo -m "gemini-3-flash-preview" -p "$(cat AGENT_PROMPT.md)" 2>&1 | tee "$LOGFILE"
    
    RESULT=$?

    # Kontrola chyb a limitů
    if grep -qE "Quota exceeded|daily quota" "$LOGFILE"; then
        echo "[$(date +%T)] Denní kvóta vyčerpána. Čekám 1 hodinu..."
        sleep 3600
    elif [ $RESULT -eq 41 ]; then
        echo "[$(date +%T)] Chyba: CLI vyžaduje API klíč (OAuth selhal). Zkuste 'gemini login'."
        sleep 300
    elif [ $RESULT -ne 0 ]; then
        echo "[$(date +%T)] Agent skončil s chybou (exit $RESULT). Čekám 60 sekund..."
        sleep 60
    else
        echo "[$(date +%T)] Krok dokončen úspěšně."
        sleep 30
    fi
done
