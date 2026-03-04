import json
from typing import Dict, Any, Union, List
import os

class JsonConfigMerger:
    """
    Ein intelligenter JSON-Konfigurations-Merger.

    Diese Klasse bietet Methoden zum Laden, Speichern und Zusammenführen von JSON-Konfigurationen.
    Unterstützt verschiedene Zusammenführungsstrategien wie 'deep_merge' und 'overwrite'.
    """

    def __init__(self, merge_strategy: str = "deep_merge") -> None:
        """
        Initialisiert den JsonConfigMerger mit einer bestimmten Zusammenführungsstrategie.

        Args:
            merge_strategy (str): Die Standard-Zusammenführungsstrategie. Gültige Werte sind
                                  'deep_merge' (Standard) und 'overwrite'.
        """
        # Speichert die gewählte Zusammenführungsstrategie
        if merge_strategy not in ["deep_merge", "overwrite"]:
            raise ValueError("Ungültige Zusammenführungsstrategie. Erlaubt sind 'deep_merge' und 'overwrite'.")
        self.merge_strategy = merge_strategy

    def load_json(self, file_path: str) -> Dict[str, Any]:
        """
        Lädt eine JSON-Konfiguration aus einer Datei.

        Args:
            file_path (str): Der Pfad zur JSON-Datei.

        Returns:
            Dict[str, Any]: Das geladene JSON als Python-Wörterbuch.

        Raises:
            FileNotFoundError: Wenn die angegebene Datei nicht existiert.
            json.JSONDecodeError: Wenn der Dateiinhalt kein gültiges JSON ist.
        """
        # Prüft, ob die Datei existiert, bevor versucht wird, sie zu öffnen
        if not os.path.exists(file_path):
            # Erzeugt einen Fehler, wenn die Datei nicht gefunden wird
            raise FileNotFoundError(f"Die Konfigurationsdatei wurde nicht gefunden: {file_path}")
        try:
            # Öffnet die Datei im Lesemodus
            with open(file_path, 'r', encoding='utf-8') as f:
                # Lädt den JSON-Inhalt und gibt ihn zurück
                return json.load(f)
        except json.JSONDecodeError as e:
            # Fängt Fehler beim Parsen von JSON ab
            raise json.JSONDecodeError(f"Fehler beim Dekodieren der JSON-Datei {file_path}: {e.msg}", e.doc, e.pos)

    def save_json(self, config: Dict[str, Any], file_path: str, indent: int = 4) -> None:
        """
        Speichert ein Python-Wörterbuch als JSON-Konfiguration in einer Datei.

        Args:
            config (Dict[str, Any]): Das zu speichernde Wörterbuch.
            file_path (str): Der Pfad, unter dem die JSON-Datei gespeichert werden soll.
            indent (int): Die Anzahl der Leerzeichen für die Einrückung in der JSON-Ausgabe.
        """
        # Öffnet die Datei im Schreibmodus
        with open(file_path, 'w', encoding='utf-8') as f:
            # Schreibt das Wörterbuch als formatiertes JSON in die Datei
            json.dump(config, f, indent=indent, ensure_ascii=False)

    def merge_configs(self, base_config: Dict[str, Any], overlay_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt zwei Konfigurationen basierend auf der initialisierten Strategie zusammen.

        Args:
            base_config (Dict[str, Any]): Die Basiskonfiguration, die überschrieben oder ergänzt wird.
            overlay_config (Dict[str, Any]): Die Overlay-Konfiguration, deren Werte angewendet werden.

        Returns:
            Dict[str, Any]: Die resultierende zusammengeführte Konfiguration.
        """
        # Wählt die entsprechende Zusammenführungsfunktion basierend auf der Strategie
        if self.merge_strategy == "deep_merge":
            # Ruft die Methode für tiefes Zusammenführen auf
            return self._deep_merge(base_config, overlay_config)
        elif self.merge_strategy == "overwrite":
            # Ruft die Methode für einfaches Überschreiben auf
            return self._overwrite_merge(base_config, overlay_config)
        else:
            # Dies sollte aufgrund der __init__-Validierung nicht erreicht werden
            raise ValueError(f"Unbekannte Zusammenführungsstrategie: {self.merge_strategy}")

    def _deep_merge(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt zwei Wörterbücher rekursiv zusammen (tiefer Merge).

        Wenn ein Schlüssel in beiden Wörterbüchern existiert:
        - Sind beide Werte Wörterbücher, werden sie rekursiv zusammengeführt.
        - Sind beide Werte Listen, wird die Basisliste durch die Overlay-Liste ersetzt.
        - Andernfalls (Skalare, unterschiedliche Typen) wird der Wert aus dem Overlay genommen.
        Wenn ein Schlüssel nur im Overlay existiert, wird er zur Basis hinzugefügt.

        Args:
            base (Dict[str, Any]): Das Basis-Wörterbuch.
            overlay (Dict[str, Any]): Das Overlay-Wörterbuch.

        Returns:
            Dict[str, Any]: Das tief zusammengeführte Wörterbuch.
        """
        # Erstellt eine Kopie des Basis-Wörterbuchs, um das Original nicht zu ändern
        merged = base.copy()
        # Iteriert über alle Schlüssel-Wert-Paare im Overlay-Wörterbuch
        for key, value in overlay.items():
            # Prüft, ob der Schlüssel auch im Basis-Wörterbuch existiert
            if key in merged:
                # Wenn beide Werte Wörterbücher sind, führe sie rekursiv zusammen
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = self._deep_merge(merged[key], value)
                # Wenn beide Werte Listen sind, ersetze die Basisliste durch die Overlay-Liste
                # Dies ist eine gängige Strategie für Konfigurationsmerges, wo Listen oft komplett ersetzt werden
                elif isinstance(merged[key], list) and isinstance(value, list):
                    merged[key] = value
                # Andernfalls (Skalare, unterschiedliche Typen), überschreibe den Basiswert mit dem Overlay-Wert
                else:
                    merged[key] = value
            else:
                # Wenn der Schlüssel nicht in der Basis existiert, füge ihn aus dem Overlay hinzu
                merged[key] = value
        # Gibt das zusammengeführte Wörterbuch zurück
        return merged

    def _overwrite_merge(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt zwei Wörterbücher zusammen, wobei Werte aus dem Overlay die Basiswerte überschreiben.
        Dies ist ein flacher Merge, der keine Rekursion für verschachtelte Wörterbücher durchführt.

        Args:
            base (Dict[str, Any]): Das Basis-Wörterbuch.
            overlay (Dict[str, Any]): Das Overlay-Wörterbuch.

        Returns:
            Dict[str, Any]: Das zusammengeführte Wörterbuch mit überschriebenen Werten.
        """
        # Erstellt eine Kopie der Basis und aktualisiert sie mit dem Overlay
        # Dies überschreibt bestehende Schlüssel und fügt neue hinzu
        merged = base.copy()
        merged.update(overlay)
        return merged

if __name__ == "__main__":
    # Beispielnutzung des JsonConfigMergers

    # Erstelle temporäre JSON-Dateien für das Beispiel
    base_config_data = {
        "app_name": "MyWebApp",
        "version": "1.0.0",
        "settings": {
            "debug": True,
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

    overlay_config_data = {
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

    # Definiere Dateipfade
    base_file = "base_config.json"
    overlay_file = "overlay_config.json"
    merged_deep_file = "merged_deep_config.json"
    merged_overwrite_file = "merged_overwrite_config.json"

    merger = JsonConfigMerger()

    # Speichere die Basis- und Overlay-Konfigurationen
    merger.save_json(base_config_data, base_file)
    merger.save_json(overlay_config_data, overlay_file)
    print(f"Basis-Konfiguration gespeichert in {base_file}")
    print(f"Overlay-Konfiguration gespeichert in {overlay_file}\n")

    # Lade die Konfigurationen
    base = merger.load_json(base_file)
    overlay = merger.load_json(overlay_file)

    # Führe mit 'deep_merge' Strategie zusammen
    print("Führe Konfigurationen mit 'deep_merge' zusammen:")
    merger.merge_strategy = "deep_merge"
    merged_deep = merger.merge_configs(base, overlay)
    merger.save_json(merged_deep, merged_deep_file)
    print(json.dumps(merged_deep, indent=4))
    print(f"Zusammengeführte Konfiguration (deep_merge) gespeichert in {merged_deep_file}\n")

    # Lade die Konfigurationen erneut für den nächsten Merge
    base = merger.load_json(base_file)
    overlay = merger.load_json(overlay_file)

    # Führe mit 'overwrite' Strategie zusammen
    print("Führe Konfigurationen mit 'overwrite' zusammen:")
    merger.merge_strategy = "overwrite"
    merged_overwrite = merger.merge_configs(base, overlay)
    merger.save_json(merged_overwrite, merged_overwrite_file)
    print(json.dumps(merged_overwrite, indent=4))
    print(f"Zusammengeführte Konfiguration (overwrite) gespeichert in {merged_overwrite_file}\n")

    # Aufräumen der temporären Dateien
    os.remove(base_file)
    os.remove(overlay_file)
    os.remove(merged_deep_file)
    os.remove(merged_overwrite_file)
    print("Temporäre Dateien aufgeräumt.")
