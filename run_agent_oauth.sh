#!/bin/bash

# Project Directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Create logs directory if missing
mkdir -p agent_logs

# Saturnin: Unset API Key to use OAuth profile in Gemini CLI.
unset GEMINI_API_KEY

# Android SDK Setup
export ANDROID_HOME="/home/fila/android-sdk"
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"

# Activation of virtual environment (if applicable)
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "--- Saturnin's Agent (OAuth) for Žolíky is starting ---"

while true; do
    COMMIT=$(git rev-parse --short=6 HEAD 2>/dev/null || echo "init")
    LOGFILE="agent_logs/agent_${COMMIT}_$(date +%s).log"

    echo "[$(date +%T)] Running agent step via OAuth..."
    
    # Run gemini with agent prompt
    gemini --yolo -m "gemini-3-flash-preview" -p "$(cat AGENT_PROMPT.md)" 2>&1 | tee "$LOGFILE"
    
    RESULT=$?

    # Error and Quota handling
    if grep -qE "Quota exceeded|daily quota" "$LOGFILE"; then
        echo "[$(date +%T)] Daily quota exceeded. Waiting 1 hour..."
        sleep 3600
    elif [ $RESULT -eq 41 ]; then
        echo "[$(date +%T)] Error: CLI requires API Key (OAuth failed). Try 'gemini login'."
        sleep 300
    elif [ $RESULT -ne 0 ]; then
        echo "[$(date +%T)] Agent exited with error (exit $RESULT). Waiting 60 seconds..."
        sleep 60
    else
        echo "[$(date +%T)] Step completed successfully."
        sleep 30
    fi
done
