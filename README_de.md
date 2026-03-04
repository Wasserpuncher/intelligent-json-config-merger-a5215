# Intelligenter JSON-Konfigurations-Merger

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Lizenz](https://img.shields.io/badge/License-MIT-green.svg)
![Build Status](https://github.com/your-username/intelligent-json-config-merger/actions/workflows/python-app.yml/badge.svg)

Eine unternehmenstaugliche, quelloffene Python-Bibliothek zum intelligenten Zusammenführen von JSON-Konfigurationsdateien. Dieses Tool wurde entwickelt, um das Anwendungs-Konfigurationsmanagement zu vereinfachen, indem es robuste Strategien zur Kombination mehrerer JSON-Quellen bietet und so einen flexiblen und hierarchischen Ansatz für Einstellungen gewährleistet.

## Funktionen

*   **Intelligenter Tiefen-Merge**: Führt verschachtelte Dictionaries rekursiv zusammen und ermöglicht eine feingranulare Kontrolle über die Konfigurationsvererbung. Bei Konflikten von Skalarwerten hat das Overlay Vorrang. Bei Listen ersetzt die Overlay-Liste die Basisliste vollständig, was eine klare Überschreibungsstrategie für array-basierte Konfigurationen bietet.
*   **Einfacher Überschreibungs-Merge**: Eine unkomplizierte Merge-Strategie, bei der alle Werte aus der Overlay-Konfiguration direkt entsprechende Werte in der Basiskonfiguration überschreiben, ohne Rekursion.
*   **Dateieingabe/-ausgabe**: Praktische Methoden zum Laden von JSON aus Dateien und zum Speichern zusammengeführter Konfigurationen zurück in Dateien.
*   **Type Hinting & OOP**: Entwickelt mit modernen Python-Praktiken, einschließlich Typ-Hinweisen für Klarheit und einer Objektorientierten Programmierung (OOP)-Struktur für Wartbarkeit und Erweiterbarkeit.
*   **Zweisprachige Dokumentation**: Umfassende Dokumentation in Englisch und Deutsch verfügbar.

## Inhaltsverzeichnis

1.  [Installation](#1-installation)
2.  [Nutzung](#2-nutzung)
    *   [Grundlegender Merge](#grundlegender-merge)
    *   [Tiefen-Merge-Strategie](#tiefen-merge-strategie)
    *   [Überschreibungs-Merge-Strategie](#überschreibungs-merge-strategie)
3.  [Architektur](#3-architektur)
4.  [Mitwirken](#4-mitwirken)
5.  [Lizenz](#5-lizenz)

## 1. Installation

Um zu beginnen, klonen Sie das Repository und installieren Sie die erforderlichen Abhängigkeiten:

```bash
git clone https://github.com/your-username/intelligent-json-config-merger.git
cd intelligent-json-config-merger
python -m venv venv
source venv/bin/activate  # Unter Windows: `venv\Scripts\activate`
pip install -r requirements.txt
```

## 2. Nutzung

So können Sie den `JsonConfigMerger` in Ihren Python-Projekten verwenden.

### Grundlegender Merge

Zuerst erstellen wir einige Beispiel-Konfigurationsdateien:

`base_config.json`:
```json
{
    "app_name": "MyWebApp",
    "version": "1.0.0",
    "settings": {
        "debug": true,
        "port": 8080,
        "database": {
            "host": "localhost",
            "user": "admin"
        },
        "features": ["featureA", "featureB"]
    },
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
}
```

`overlay_config.json`:
```json
{
    "version": "1.1.0",
    "settings": {
        "port": 9000,
        "database": {
            "host": "prod-db",
            "password": "secret"
        },
        "features": ["featureC", "featureD"]
    },
    "new_key": "new_value",
    "users": [
        {"id": 3, "name": "Charlie"}
    ]
}
```

Nun können Sie die `JsonConfigMerger`-Klasse verwenden:

```python
from main import JsonConfigMerger
import json
import os

# Erstellen Sie temporäre Dateien zur Demonstration
with open('base_config.json', 'w') as f:
    json.dump({
        "app_name": "MyWebApp", "version": "1.0.0",
        "settings": {"debug": True, "port": 8080, "database": {"host": "localhost", "user": "admin"}, "features": ["featureA", "featureB"]},
        "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    }, f, indent=4)

with open('overlay_config.json', 'w') as f:
    json.dump({
        "version": "1.1.0",
        "settings": {"port": 9000, "database": {"host": "prod-db", "password": "secret"}, "features": ["featureC", "featureD"]},
        "new_key": "new_value",
        "users": [{"id": 3, "name": "Charlie"}]
    }, f, indent=4)

merger = JsonConfigMerger()

# Konfigurationen laden
base = merger.load_json('base_config.json')
overlay = merger.load_json('overlay_config.json')

# --- Beispiel für Tiefen-Merge ---
merger.merge_strategy = "deep_merge"
merged_deep = merger.merge_configs(base, overlay)
print("\nTief zusammengeführte Konfiguration:")
print(json.dumps(merged_deep, indent=4))
merger.save_json(merged_deep, 'merged_deep_config.json')

# --- Beispiel für Überschreibungs-Merge (Basis/Overlay neu laden, da sie möglicherweise durch den Tiefen-Merge geändert wurden) ---
base_for_overwrite = merger.load_json('base_config.json')
overlay_for_overwrite = merger.load_json('overlay_config.json')

merger.merge_strategy = "overwrite"
merged_overwrite = merger.merge_configs(base_for_overwrite, overlay_for_overwrite)
print("\nÜberschrieben zusammengeführte Konfiguration:")
print(json.dumps(merged_overwrite, indent=4))
merger.save_json(merged_overwrite, 'merged_overwrite_config.json')

# Temporäre Dateien aufräumen
os.remove('base_config.json')
os.remove('overlay_config.json')
os.remove('merged_deep_config.json')
os.remove('merged_overwrite_config.json')
```

### Tiefen-Merge-Strategie

Wenn `merge_strategy` auf `"deep_merge"` gesetzt ist:

*   **Dictionaries**: Verschachtelte Dictionaries werden rekursiv zusammengeführt. Schlüssel, die in beiden vorhanden sind, werden gemergt; Schlüssel, die nur im Overlay vorhanden sind, werden hinzugefügt.
*   **Listen**: Wenn ein Schlüssel einer Liste sowohl in der Basis als auch im Overlay entspricht, wird die gesamte Basisliste durch die Overlay-Liste *ersetzt*.
*   **Skalarwerte (Strings, Zahlen, Booleans, Null)**: Overlay-Werte überschreiben Basiswerte.

Ergebnis für `merged_deep_config.json` (aus obigem Beispiel):

```json
{
    "app_name": "MyWebApp",
    "version": "1.1.0",
    "settings": {
        "debug": true,
        "port": 9000,
        "database": {
            "host": "prod-db",
            "user": "admin",
            "password": "secret"
        },
        "features": [
            "featureC",
            "featureD"
        ]
    },
    "users": [
        {
            "id": 3,
            "name": "Charlie"
        }
    ],
    "new_key": "new_value"
}
```

### Überschreibungs-Merge-Strategie

Wenn `merge_strategy` auf `"overwrite"` gesetzt ist:

*   Alle Top-Level-Schlüssel in der Overlay-Konfiguration überschreiben direkt ihre Gegenstücke in der Basiskonfiguration. Wenn ein Wert im Overlay ein Dictionary oder eine Liste ist, ersetzt er den entsprechenden Basiswert vollständig, ohne rekursives Zusammenführen.

Ergebnis für `merged_overwrite_config.json` (aus obigem Beispiel):

```json
{
    "app_name": "MyWebApp",
    "version": "1.1.0",
    "settings": {
        "port": 9000,
        "database": {
            "host": "prod-db",
            "password": "secret"
        },
        "features": [
            "featureC",
            "featureD"
        ]
    },
    "users": [
        {
            "id": 3,
            "name": "Charlie"
        }
    ],
    "new_key": "new_value"
}
```

## 3. Architektur

Für einen detaillierten Einblick in die Designprinzipien, Kernkomponenten und Erweiterbarkeit des `JsonConfigMerger` lesen Sie bitte die [Architektur-Dokumentation](docs/architecture_de.md).

## 4. Mitwirken

Wir freuen uns über Beiträge! Bitte beachten Sie unsere [CONTRIBUTING.md](CONTRIBUTING.md) für Richtlinien zum Einreichen von Fehlerberichten, Feature-Anfragen und Code-Beiträgen.

## 5. Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Details finden Sie in der Datei [LICENSE](LICENSE).
