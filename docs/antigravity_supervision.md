# Instruxe pro dohled nad Antigravity (Saturninův protokol)

Tento protokol se spouští pokaždé, když pan Filip vydá pokyn k inspekci po práci agenta v Antigravity.

## Průběh inspekce

### 1. Git Revize
- Zkontrolovat `git status` a `git diff`.
- Identifikovat všechny provedené změny v kódu (`src/`), testech (`tests/`) i dokumentaci.
- Pokud agent zapomněl práci uložit, provést `git add .` a `git commit -m "..."`.

### 2. Task Management
- Porovnat provedené změny se soubory v `current_tasks/`.
- Splněné úkoly přesunout do `completed_tasks/`.
- Ověřit bilingválnost komentářů (angličtina + čeština).

### 3. Dokumentace
- Aktualizovat `README.md` a `docs/architecture.md` / `docs/z80_reference.md` podle nových funkcí.

### 4. Hloubkový Brain Scan (Klíčový krok)
- **Cesta:** `~/.gemini/antigravity/brain/`
- **Povinnost:** Přečíst poslední verze (včetně `.resolved.X`) souborů:
    - `task.md`
    - `walkthrough.md`
    - `implementation_plan.md`
- **Analýza:** Hledat "Next Steps", "TODO", "Unfinished" nebo nezaškrtnuté položky v seznamech úkolů.
- **Akce:** Jakýkoliv nalezený rest nebo budoucí plán okamžitě přetavit do nového `.md` souboru v `current_tasks/`.

### 5. Čištění
- Ukončit všechny případné zapomenuté procesy `run_agent.sh` nebo `gemini`.

---
*Vytvořeno 9. února 2026 na pokyn pana Filipa.*
