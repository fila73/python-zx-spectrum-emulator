#!/bin/bash
# Žolíky - Agent Start Script

PROJECT_DIR="/home/fila/projects/android/zoliky"
echo "--- Inicializace vývoje hry Žolíky ---"
echo "Adresář: $PROJECT_DIR"

# Kontrola závislostí (v budoucnu Gradle/Android SDK)
if ! command -v git &> /dev/null; then
    echo "Varování: git není nainstalován."
fi

echo "Stav projektu:"
ls -R $PROJECT_DIR/current_tasks
echo "--------------------------------------"
echo "Saturnin je připraven k asistenci."
