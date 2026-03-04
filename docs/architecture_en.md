# Architecture of the Intelligent JSON Config Merger

This document provides a deep dive into the architectural design and implementation details of the `Intelligent JSON Config Merger`. It outlines the core components, design principles, merge strategies, and potential areas for future expansion.

## Table of Contents

1.  [Purpose and Design Principles](#1-purpose-and-design-principles)
2.  [Core Components](#2-core-components)
    *   [`JsonConfigMerger` Class](#jsonconfigmerger-class)
    *   [`load_json` and `save_json` Methods](#load_json-and-save_json-methods)
    *   [`merge_configs` Dispatcher](#merge_configs-dispatcher)
3.  [Merge Strategies](#3-merge-strategies)
    *   [`_deep_merge` Strategy](#_deep_merge-strategy)
    *   [`_overwrite_merge` Strategy](#_overwrite_merge-strategy)
4.  [Extensibility](#4-extensibility)
5.  [Future Enhancements](#5-future-enhancements)

## 1. Purpose and Design Principles

### Purpose

The primary purpose of the `Intelligent JSON Config Merger` is to provide a robust and flexible solution for managing application configurations across different environments (e.g., development, staging, production) or for layering configurations (e.g., default settings, user-specific overrides). It aims to simplify the process of combining multiple JSON sources into a single, coherent configuration object.

### Design Principles

*   **Clarity and Simplicity**: The codebase should be easy to understand and maintain, even for beginners. This is achieved through clear naming, docstrings, type hints, and well-defined method responsibilities.
*   **Modularity**: Components are designed to be self-contained and focused on a single responsibility (e.g., loading, saving, merging). This allows for easier testing, modification, and extension.
*   **Flexibility**: The system should support different merging behaviors through configurable strategies, allowing users to choose the approach that best suits their needs.
*   **Robustness**: Error handling for file operations and JSON parsing is crucial to ensure the tool behaves predictably under various conditions.
*   **Bilingual Support**: Code comments are in German to support German-speaking beginners, while public documentation and docstrings are in English for broader appeal.

## 2. Core Components

The project revolves around the `JsonConfigMerger` class, which encapsulates all configuration management logic.

### `JsonConfigMerger` Class

This is the main entry point for using the library. It's initialized with a default merge strategy, which can be changed at runtime. It orchestrates the loading, saving, and merging operations.

*   **`__init__(self, merge_strategy: str = "deep_merge") -> None`**:
    *   Initializes the merger with a specified `merge_strategy`. Valid strategies are currently `"deep_merge"` and `"overwrite"`. An `ValueError` is raised for invalid strategies, ensuring the class is always in a valid state.
    *   Stores the chosen strategy in `self.merge_strategy`.

### `load_json` and `save_json` Methods

These utility methods handle the interaction with the file system, abstracting away the details of reading from and writing to JSON files.

*   **`load_json(self, file_path: str) -> Dict[str, Any]`**:
    *   Takes a `file_path` as input.
    *   Performs a check (`os.path.exists`) to ensure the file exists before attempting to open it, raising a `FileNotFoundError` if not.
    *   Opens the file in read mode (`'r'`) with `utf-8` encoding.
    *   Uses `json.load()` to parse the file content into a Python dictionary.
    *   Includes robust error handling for `json.JSONDecodeError` to catch malformed JSON files.

*   **`save_json(self, config: Dict[str, Any], file_path: str, indent: int = 4) -> None`**:
    *   Takes a Python `config` dictionary and a `file_path`.
    *   Opens the file in write mode (`'w'`) with `utf-8` encoding.
    *   Uses `json.dump()` to serialize the dictionary to JSON. The `indent=4` argument ensures human-readable formatting, and `ensure_ascii=False` allows for non-ASCII characters directly in the output.

### `merge_configs` Dispatcher

This public method serves as the orchestrator for applying the chosen merge strategy.

*   **`merge_configs(self, base_config: Dict[str, Any], overlay_config: Dict[str, Any]) -> Dict[str, Any]`**:
    *   Accepts `base_config` (the initial configuration) and `overlay_config` (the configuration to apply on top).
    *   Based on `self.merge_strategy`, it dispatches the call to the appropriate private merge helper method (`_deep_merge` or `_overwrite_merge`).
    *   This design allows for easy addition of new merge strategies in the future without modifying the core dispatch logic significantly.

## 3. Merge Strategies

The intelligence of the merger lies in its merge strategies. Each strategy defines how conflicts and additions are handled when combining two configuration dictionaries.

### `_deep_merge` Strategy

This strategy is designed for hierarchical configurations where nested structures should be intelligently combined.

*   **Behavior**: It performs a recursive merge of dictionaries. If a key exists in both `base` and `overlay`:
    *   **Dictionaries**: If both values are dictionaries, `_deep_merge` is called recursively on them. This ensures that nested configurations are merged rather than simply overwritten.
    *   **Lists**: If both values are lists, the `base` list is *completely replaced* by the `overlay` list. This is a common and often desired behavior in configuration management, where an overlay list is intended to define the complete set of items rather than appending or complex merging of individual list elements.
    *   **Scalar Values (and type changes)**: If the values are scalars (strings, numbers, booleans, null) or if their types differ (e.g., a dictionary in `base` becomes a string in `overlay`), the value from the `overlay` configuration takes precedence and overwrites the `base` value.
*   **New Keys**: If a key exists only in the `overlay` configuration, it is added to the merged result.
*   **Implementation**: A copy of the `base` dictionary is made initially to ensure the original `base_config` object is not mutated. The merge logic then iterates through the `overlay` keys and applies the rules described above.

### `_overwrite_merge` Strategy

This strategy provides a simpler, non-recursive merge.

*   **Behavior**: It performs a shallow merge where all top-level keys present in the `overlay` configuration will directly overwrite their counterparts in the `base` configuration. Keys only present in `base` remain; keys only in `overlay` are added.
*   **Implementation**: It leverages Python's `dict.update()` method on a copy of the base dictionary, providing an efficient and straightforward implementation for this strategy.

## 4. Extensibility

The current architecture is designed with extensibility in mind:

*   **New Merge Strategies**: To add a new merge strategy (e.g., `"append_lists"`, `"merge_lists_by_key"`, `"strict_no_new_keys"`):
    1.  Implement a new private method (e.g., `_my_new_merge_strategy`) within the `JsonConfigMerger` class, containing the specific logic.
    2.  Add the new strategy name to the `__init__` method's validation list.
    3.  Add a new `elif` branch in the `merge_configs` method to dispatch to the new private method when `self.merge_strategy` matches the new strategy's name.
*   **Custom Load/Save Formats**: While currently focused on JSON, the `load_json` and `save_json` methods could be extended or replaced by `load_yaml`, `save_toml`, etc., by creating new methods and potentially a `format` parameter in the constructor or `load`/`save` methods.

## 5. Future Enhancements

*   **Advanced List Merging**: Implement more sophisticated list merging options (e.g., appending unique items, merging lists of objects based on a common key like `id`). This would require additional parameters to `_deep_merge` or a dedicated list merging helper.
*   **Schema Validation**: Integrate with a JSON Schema validation library (e.g., `jsonschema`) to validate configurations against a defined schema before or after merging.
*   **Merge Hooks/Callbacks**: Allow users to register custom functions that are called at specific points during the merge process (e.g., before merging a specific key, after a conflict resolution).
*   **Command-Line Interface (CLI)**: Provide a command-line tool for easy merging of files without writing Python code.
*   **Configuration Source Abstraction**: Abstract configuration sources beyond just files (e.g., environment variables, databases, remote URLs).
