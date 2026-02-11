#!/bin/bash
# Žolíky - Agent Start Script

PROJECT_DIR="/home/fila/projects/android/zoliky"
echo "--- Inicializace vývoje hry Žolíky ---"
echo "Adresář: $PROJECT_DIR"

# Source SDKMAN
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"

# Kontrola nástrojů
echo "Kontrola vývojového prostředí:"
if command -v kotlinc &> /dev/null; then
    echo "Kotlin: $(kotlinc -version)"
else
    echo "CHYBA: Kotlin není nainstalován!"
fi

if command -v gradle &> /dev/null; then
    echo "Gradle: $(gradle -version | grep Gradle | head -n 1)"
else
    echo "CHYBA: Gradle není nainstalován!"
fi

if ! command -v git &> /dev/null; then
    echo "Varování: git není nainstalován."
fi

echo "Stav projektu:"
ls -R $PROJECT_DIR/current_tasks
echo "--------------------------------------"
echo "Saturnin je připraven k asistenci."
