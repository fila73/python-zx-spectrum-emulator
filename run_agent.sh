#!/bin/bash

# Adresář projektu
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Vytvoření složky pro logy, pokud neexistuje
mkdir -p agent_logs

# Nastavení API klíče pro Gemini CLI
# Pozor: Klíč je vložen přímo, v produkci by měl být v environmentu
export GEMINI_API_KEY="AIzaSyCjUP0lI0Bho8cpecznstmIoDz_UzRKP_g"

# Aktivace virtuálního prostředí
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "--- Saturninův agent (v2) startuje ---"

while true; do
    COMMIT=$(git rev-parse --short=6 HEAD 2>/dev/null || echo "init")
    LOGFILE="agent_logs/agent_${COMMIT}_$(date +%s).log"

    echo "[$(date +%T)] Běží krok agenta..."
    
    # Spuštění gemini s modelem gemini-3-flash-preview
    # Přidán --debug pro detailnější info v případě chyby
    gemini --yolo -m "gemini-3-flash-preview" -p "$(cat AGENT_PROMPT.md)" > "$LOGFILE" 2>&1
    
    RESULT=$?

    # Kontrola chyb a limitů
    if grep -q "Quota exceeded" "$LOGFILE"; then
        echo "[$(date +%T)] Limit RPM dosažen. Čekám 60 sekund..."
        sleep 60
    elif [ $RESULT -ne 0 ]; then
        echo "[$(date +%T)] Agent skončil s chybou (exit $RESULT). Čekám 30 sekund..."
        sleep 30
    else
        echo "[$(date +%T)] Krok dokončen úspěšně."
        sleep 10
    fi
done
