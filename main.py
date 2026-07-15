import argparse
import json
import sys
from typing import Dict, Any, List, Optional
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


# Standardname der Merge-Steuerungsdatei, falls kein Pfad angegeben wird.
DEFAULT_CONFIG_FILENAME = "config.json"


class MergeRunConfig:
    """
    Repräsentiert einen kompletten, aus einer JSON-Steuerungsdatei geladenen Merge-Lauf.

    Die Steuerungsdatei (`config.json`) beschreibt, welche Eingabedateien gemergt
    werden, welche Strategie dabei verwendet wird und wohin das Ergebnis geschrieben
    wird -- ohne dass dafür Code angepasst werden muss.
    """

    def __init__(
        self,
        inputs: List[str],
        strategy: str = "deep_merge",
        output: Optional[str] = None,
    ) -> None:
        """
        Args:
            inputs: Geordnete Liste der zu mergenden JSON-Eingabedateien.
            strategy: Merge-Strategie ('deep_merge' oder 'overwrite').
            output: Optionaler Pfad, in den das Ergebnis geschrieben wird.
        """
        self.inputs = inputs
        self.strategy = strategy
        self.output = output

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MergeRunConfig":
        """
        Erzeugt eine MergeRunConfig aus einem geparsten JSON-Objekt und validiert die Felder.

        Raises:
            ValueError: Wenn Pflichtfelder fehlen oder Werte ungültig sind.
        """
        if not isinstance(data, dict):
            raise ValueError("Die Steuerungsdatei muss ein JSON-Objekt sein.")

        raw_inputs = data.get("inputs")
        if not isinstance(raw_inputs, list) or not raw_inputs:
            raise ValueError("Die Steuerungsdatei benötigt ein nicht-leeres 'inputs'-Array.")
        inputs: List[str] = []
        for item in raw_inputs:
            if not isinstance(item, str):
                raise ValueError("Jeder Eintrag in 'inputs' muss ein Dateipfad (String) sein.")
            inputs.append(item)

        strategy = data.get("strategy", "deep_merge")
        if not isinstance(strategy, str):
            raise ValueError("'strategy' muss ein String sein.")
        if strategy not in ("deep_merge", "overwrite"):
            raise ValueError("'strategy' muss 'deep_merge' oder 'overwrite' sein.")

        output = data.get("output")
        if output is not None and not isinstance(output, str):
            raise ValueError("'output' muss ein Dateipfad (String) oder null sein.")

        return MergeRunConfig(inputs=inputs, strategy=strategy, output=output)


def load_run_config(config_path: str = DEFAULT_CONFIG_FILENAME) -> MergeRunConfig:
    """
    Lädt und validiert eine Merge-Steuerungsdatei von der Festplatte.

    Raises:
        FileNotFoundError: Wenn die Steuerungsdatei fehlt.
        json.JSONDecodeError: Wenn die Steuerungsdatei kein gültiges JSON ist.
        ValueError: Wenn der Inhalt kein gültiges Merge-Schema beschreibt.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Steuerungsdatei nicht gefunden: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return MergeRunConfig.from_dict(data)


def run_from_config(config_path: str = DEFAULT_CONFIG_FILENAME) -> Dict[str, Any]:
    """
    Führt einen kompletten Merge anhand einer Steuerungsdatei aus.

    Lädt der Reihe nach alle Eingabedateien, mergt sie mit der konfigurierten
    Strategie und schreibt das Ergebnis -- falls angegeben -- in die Ausgabedatei.
    Gibt die zusammengeführte Konfiguration zurück.
    """
    run_config = load_run_config(config_path)
    merger = JsonConfigMerger(merge_strategy=run_config.strategy)
    result: Dict[str, Any] = {}
    for input_path in run_config.inputs:
        overlay = merger.load_json(input_path)
        result = merger.merge_configs(result, overlay)
    if run_config.output is not None:
        merger.save_json(result, run_config.output)
    return result


def main(argv: Optional[List[str]] = None) -> int:
    """
    Kommandozeilen-Einstiegspunkt: steuert einen Merge über eine JSON-Steuerungsdatei.
    """
    parser = argparse.ArgumentParser(
        description="Merge JSON configuration files driven by a JSON control file.",
    )
    parser.add_argument(
        "-c",
        "--config",
        default=DEFAULT_CONFIG_FILENAME,
        help=f"Path to the merge control file (default: {DEFAULT_CONFIG_FILENAME}).",
    )
    args = parser.parse_args(argv)
    try:
        result = run_from_config(args.config)
    except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=4, ensure_ascii=False))
    return 0


def _run_demo() -> None:
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


if __name__ == "__main__":
    sys.exit(main())
