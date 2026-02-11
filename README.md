# Projekt: Žolíky (Android)

Mobilní hra pro Android implementující klasickou karetní hru Žolíky.

## Vize projektu
Vytvořit moderní, svižnou a společenskou hru, která umožní:
- Hru proti AI protihráčům (offline).
- Lokální hru na jednom zařízení (pass-and-play).
- Online multiplayer přes internet.

## Zvolený Framework: Kotlin + Jetpack Compose
Pro vývoj jsme zvolili nativní cestu pomocí **Kotlinu** a moderního UI frameworku **Jetpack Compose**.
- **Proč:** Maximální výkon, přístup k nejnovějším Android API, moderní deklarativní UI, skvělá podpora Google.

## Pravidla (Stručný přehled)
- **Karty:** 2 sady po 52 kartách + 4 žolíci (celkem 108 karet).
- **Cíl:** Zbavit se všech karet v ruce vykládáním postupových řad (sekvencí) nebo skupin stejných hodnot.
- **Vykládání:** První vyložení musí mít hodnotu alespoň 42 bodů (včetně čisté postupky).
- **Žolík:** Nahrazuje jakoukoli kartu. Lze jej v postupce nahradit pravou kartou a vzít zpět do ruky.

## Struktura projektu
- `src/`: Zdrojový kód (Kotlin/Compose).
- `assets/`: Grafické podklady, zvuky, definice karet.
- `docs/`: Detailní specifikace pravidel a architektury.
- `current_tasks/`: Aktivní úkoly pro agenty.
- `completed_tasks/`: Historie hotových úkolů.
- `agent_logs/`: Záznamy z vývoje.

---
*Vytvořeno Saturninem pro Filipa.*
