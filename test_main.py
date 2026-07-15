import unittest
import json
import os
import tempfile
import shutil
from main import (
    JsonConfigMerger,
    MergeRunConfig,
    load_run_config,
    run_from_config,
    main,
)

class TestJsonConfigMerger(unittest.TestCase):
    """
    Testsuite für die JsonConfigMerger-Klasse.
    """

    def setUp(self) -> None:
        """
        Setzt die Testumgebung auf, indem eine Instanz des Mergers erstellt wird
        und temporäre Dateipfade definiert werden.
        """
        # Erstellt eine Instanz des Mergers für jeden Test
        self.merger = JsonConfigMerger()
        # Definiert Dateinamen für temporäre Dateien
        self.base_file = "temp_base_config.json"
        self.overlay_file = "temp_overlay_config.json"
        self.output_file = "temp_output_config.json"

    def tearDown(self) -> None:
        """
        Räumt nach jedem Test auf, indem alle temporären Dateien gelöscht werden.
        """
        # Liste der zu löschenden Dateien
        for f in [self.base_file, self.overlay_file, self.output_file]:
            # Prüft, ob die Datei existiert, bevor sie gelöscht wird
            if os.path.exists(f):
                os.remove(f)

    def _create_json_file(self, file_path: str, data: dict) -> None:
        """
        Hilfsmethode zum Erstellen einer temporären JSON-Datei.
        """
        # Öffnet die Datei im Schreibmodus und speichert die Daten als JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def test_load_json_success(self) -> None:
        """
        Testet das erfolgreiche Laden einer JSON-Datei.
        """
        # Beispieldaten
        test_data = {"key": "value", "number": 123}
        # Erstellt eine temporäre JSON-Datei
        self._create_json_file(self.base_file, test_data)
        # Lädt die Datei und prüft, ob der Inhalt korrekt ist
        loaded_data = self.merger.load_json(self.base_file)
        self.assertEqual(loaded_data, test_data)

    def test_load_json_file_not_found(self) -> None:
        """
        Testet das Laden einer nicht existierenden JSON-Datei.
        """
        # Erwartet, dass ein FileNotFoundError ausgelöst wird
        with self.assertRaises(FileNotFoundError):
            self.merger.load_json("non_existent_file.json")

    def test_load_json_invalid_format(self) -> None:
        """
        Testet das Laden einer Datei mit ungültigem JSON-Format.
        """
        # Schreibt ungültiges JSON in eine Datei
        with open(self.base_file, 'w', encoding='utf-8') as f:
            f.write("{'key': 'value'") # Ungültiges JSON
        # Erwartet, dass ein JSONDecodeError ausgelöst wird
        with self.assertRaises(json.JSONDecodeError):
            self.merger.load_json(self.base_file)

    def test_save_json_success(self) -> None:
        """
        Testet das erfolgreiche Speichern einer JSON-Datei.
        """
        # Beispieldaten
        test_data = {"key": "value", "list": [1, 2, 3]}
        # Speichert die Daten in einer Datei
        self.merger.save_json(test_data, self.output_file)
        # Lädt die gespeicherte Datei und prüft den Inhalt
        with open(self.output_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data)

    def test_deep_merge_simple_overwrite(self) -> None:
        """
        Testet den tiefen Merge mit einfachen Überschreibungen von Skalaren.
        """
        # Basis- und Overlay-Konfigurationen
        base = {"a": 1, "b": 2}
        overlay = {"b": 3, "c": 4}
        expected = {"a": 1, "b": 3, "c": 4}
        # Führt den Merge durch und prüft das Ergebnis
        merged = self.merger._deep_merge(base, overlay)
        self.assertEqual(merged, expected)

    def test_deep_merge_nested_dicts(self) -> None:
        """
        Testet den tiefen Merge mit verschachtelten Wörterbüchern.
        """
        # Basis- und Overlay-Konfigurationen mit Verschachtelung
        base = {"settings": {"debug": True, "port": 80}}
        overlay = {"settings": {"port": 443, "timeout": 30}}
        expected = {"settings": {"debug": True, "port": 443, "timeout": 30}}
        merged = self.merger._deep_merge(base, overlay)
        self.assertEqual(merged, expected)

    def test_deep_merge_lists_replacement(self) -> None:
        """
        Testet den tiefen Merge, wobei Listen komplett ersetzt werden.
        """
        # Basis- und Overlay-Konfigurationen mit Listen
        base = {"features": ["A", "B"], "data": {"list": [1, 2]}}
        overlay = {"features": ["C", "D"], "data": {"list": [3, 4]}}
        expected = {"features": ["C", "D"], "data": {"list": [3, 4]}}
        merged = self.merger._deep_merge(base, overlay)
        self.assertEqual(merged, expected)

    def test_deep_merge_mixed_types(self) -> None:
        """
        Testet den tiefen Merge mit gemischten Typen (z.B. Dict zu Scalar).
        """
        # Basis- und Overlay-Konfigurationen mit Typänderungen
        base = {"config": {"param": "value"}}
        overlay = {"config": 123}
        expected = {"config": 123}
        merged = self.merger._deep_merge(base, overlay)
        self.assertEqual(merged, expected)

    def test_deep_merge_empty_configs(self) -> None:
        """
        Testet den tiefen Merge mit leeren Konfigurationen.
        """
        # Testfall: Leere Basis, nicht leeres Overlay
        self.assertEqual(self.merger._deep_merge({}, {"a": 1}), {"a": 1})
        # Testfall: Nicht leere Basis, leeres Overlay
        self.assertEqual(self.merger._deep_merge({"a": 1}, {}), {"a": 1})
        # Testfall: Beide leer
        self.assertEqual(self.merger._deep_merge({}, {}), {})

    def test_overwrite_merge_strategy(self) -> None:
        """
        Testet die 'overwrite' Zusammenführungsstrategie.
        """
        # Setzt die Strategie auf 'overwrite'
        self.merger.merge_strategy = "overwrite"
        base = {"a": 1, "b": {"x": 10}}
        overlay = {"b": {"y": 20}, "c": 3}
        # Bei 'overwrite' wird 'b' komplett ersetzt, keine Rekursion
        expected = {"a": 1, "b": {"y": 20}, "c": 3}
        merged = self.merger.merge_configs(base, overlay)
        self.assertEqual(merged, expected)

    def test_deep_merge_strategy_via_main_method(self) -> None:
        """
        Testet die 'deep_merge' Strategie über die Hauptmethode `merge_configs`.
        """
        # Setzt die Strategie auf 'deep_merge'
        self.merger.merge_strategy = "deep_merge"
        base = {"a": 1, "b": {"x": 10, "z": 100}, "list": [1, 2]}
        overlay = {"b": {"y": 20, "z": 101}, "c": 3, "list": [3, 4]}
        # Erwartetes Ergebnis für deep_merge (Listen werden ersetzt, Dictionaries rekursiv gemergt)
        expected = {"a": 1, "b": {"x": 10, "y": 20, "z": 101}, "list": [3, 4], "c": 3}
        merged = self.merger.merge_configs(base, overlay)
        self.assertEqual(merged, expected)

    def test_merge_strategy_validation(self) -> None:
        """
        Testet die Validierung der Zusammenführungsstrategie beim Initialisieren.
        """
        # Erwartet, dass ein ValueError ausgelöst wird, wenn eine ungültige Strategie übergeben wird
        with self.assertRaises(ValueError):
            JsonConfigMerger(merge_strategy="invalid_strategy")

class TestConfigFileSupport(unittest.TestCase):
    """
    Tests für den config.json-gesteuerten Merge-Lauf (Issue #1).
    """

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_json(self, name: str, data: object) -> str:
        path = os.path.join(self.tmpdir, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return path

    def test_from_dict_valid(self) -> None:
        cfg = MergeRunConfig.from_dict(
            {"inputs": ["a.json", "b.json"], "strategy": "overwrite", "output": "out.json"}
        )
        self.assertEqual(cfg.inputs, ["a.json", "b.json"])
        self.assertEqual(cfg.strategy, "overwrite")
        self.assertEqual(cfg.output, "out.json")

    def test_from_dict_defaults(self) -> None:
        cfg = MergeRunConfig.from_dict({"inputs": ["a.json"]})
        self.assertEqual(cfg.strategy, "deep_merge")
        self.assertIsNone(cfg.output)

    def test_from_dict_missing_inputs(self) -> None:
        with self.assertRaises(ValueError):
            MergeRunConfig.from_dict({"strategy": "deep_merge"})

    def test_from_dict_invalid_strategy(self) -> None:
        with self.assertRaises(ValueError):
            MergeRunConfig.from_dict({"inputs": ["a.json"], "strategy": "nope"})

    def test_load_run_config_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_run_config(os.path.join(self.tmpdir, "missing.json"))

    def test_run_from_config_deep_merge_writes_output(self) -> None:
        self._write_json("base.json", {"settings": {"debug": True, "port": 80}, "list": [1, 2]})
        self._write_json("overlay.json", {"settings": {"port": 443, "timeout": 30}, "list": [3]})
        output_path = os.path.join(self.tmpdir, "merged.json")
        config_path = self._write_json(
            "config.json",
            {
                "inputs": [
                    os.path.join(self.tmpdir, "base.json"),
                    os.path.join(self.tmpdir, "overlay.json"),
                ],
                "strategy": "deep_merge",
                "output": output_path,
            },
        )
        result = run_from_config(config_path)
        expected = {"settings": {"debug": True, "port": 443, "timeout": 30}, "list": [3]}
        self.assertEqual(result, expected)
        with open(output_path, "r", encoding="utf-8") as f:
            self.assertEqual(json.load(f), expected)

    def test_run_from_config_overwrite_strategy(self) -> None:
        # Bei 'overwrite' wird ein verschachteltes Dict komplett ersetzt (kein rekursiver Merge).
        self._write_json("base.json", {"a": 1, "b": {"x": 10}})
        self._write_json("overlay.json", {"b": {"y": 20}, "c": 3})
        config_path = self._write_json(
            "config.json",
            {
                "inputs": [
                    os.path.join(self.tmpdir, "base.json"),
                    os.path.join(self.tmpdir, "overlay.json"),
                ],
                "strategy": "overwrite",
            },
        )
        result = run_from_config(config_path)
        self.assertEqual(result, {"a": 1, "b": {"y": 20}, "c": 3})

    def test_main_cli_success(self) -> None:
        self._write_json("base.json", {"x": 1})
        self._write_json("over.json", {"y": 2})
        config_path = self._write_json(
            "config.json",
            {
                "inputs": [
                    os.path.join(self.tmpdir, "base.json"),
                    os.path.join(self.tmpdir, "over.json"),
                ]
            },
        )
        self.assertEqual(main(["--config", config_path]), 0)

    def test_main_cli_missing_config(self) -> None:
        self.assertEqual(main(["--config", os.path.join(self.tmpdir, "nope.json")]), 1)


if __name__ == '__main__':
    unittest.main()
