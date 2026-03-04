# Intelligent JSON Config Merger

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Build Status](https://github.com/your-username/intelligent-json-config-merger/actions/workflows/python-app.yml/badge.svg)

An enterprise-ready, open-source Python library for intelligently merging JSON configuration files. This tool is designed to simplify application configuration management by providing robust strategies for combining multiple JSON sources, ensuring a flexible and hierarchical approach to settings.

## Features

*   **Intelligent Deep Merge**: Recursively merges nested dictionaries, allowing for fine-grained control over configuration inheritance. For conflicting scalar values, the overlay takes precedence. For lists, the overlay list replaces the base list entirely, providing a clear overwrite strategy for array-based configurations.
*   **Simple Overwrite Merge**: A straightforward merge strategy where all values from the overlay configuration directly overwrite corresponding values in the base configuration, without recursion.
*   **File I/O**: Convenient methods for loading JSON from files and saving merged configurations back to files.
*   **Type Hinting & OOP**: Developed with modern Python practices, including type hints for clarity and an Object-Oriented Programming (OOP) structure for maintainability and extensibility.
*   **Bilingual Documentation**: Comprehensive documentation available in both English and German.

## Table of Contents

1.  [Installation](#1-installation)
2.  [Usage](#2-usage)
    *   [Basic Merge](#basic-merge)
    *   [Deep Merge Strategy](#deep-merge-strategy)
    *   [Overwrite Merge Strategy](#overwrite-merge-strategy)
3.  [Architecture](#3-architecture)
4.  [Contributing](#4-contributing)
5.  [License](#5-license)

## 1. Installation

To get started, clone the repository and install the required dependencies:

```bash
git clone https://github.com/your-username/intelligent-json-config-merger.git
cd intelligent-json-config-merger
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

## 2. Usage

Here's how you can use the `JsonConfigMerger` in your Python projects.

### Basic Merge

First, let's create some example configuration files:

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

Now, you can use the `JsonConfigMerger` class:

```python
from main import JsonConfigMerger
import json
import os

# Create temporary files for demonstration
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

# Load configurations
base = merger.load_json('base_config.json')
overlay = merger.load_json('overlay_config.json')

# --- Deep Merge Example ---
merger.merge_strategy = "deep_merge"
merged_deep = merger.merge_configs(base, overlay)
print("\nDeep Merged Configuration:")
print(json.dumps(merged_deep, indent=4))
merger.save_json(merged_deep, 'merged_deep_config.json')

# --- Overwrite Merge Example (reload base/overlay as they might have been modified by deep merge) ---
base_for_overwrite = merger.load_json('base_config.json')
overlay_for_overwrite = merger.load_json('overlay_config.json')

merger.merge_strategy = "overwrite"
merged_overwrite = merger.merge_configs(base_for_overwrite, overlay_for_overwrite)
print("\nOverwrite Merged Configuration:")
print(json.dumps(merged_overwrite, indent=4))
merger.save_json(merged_overwrite, 'merged_overwrite_config.json')

# Clean up temporary files
os.remove('base_config.json')
os.remove('overlay_config.json')
os.remove('merged_deep_config.json')
os.remove('merged_overwrite_config.json')
```

### Deep Merge Strategy

When `merge_strategy` is set to `"deep_merge"`:

*   **Dictionaries**: Nested dictionaries are merged recursively. Keys present in both are merged; keys only in the overlay are added.
*   **Lists**: If a key corresponds to a list in both the base and overlay, the entire base list is *replaced* by the overlay list.
*   **Scalar Values (strings, numbers, booleans, null)**: Overlay values overwrite base values.

Result for `merged_deep_config.json` (from example above):

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

### Overwrite Merge Strategy

When `merge_strategy` is set to `"overwrite"`:

*   All top-level keys in the overlay configuration will directly overwrite their counterparts in the base configuration. If a value in the overlay is a dictionary or a list, it replaces the corresponding base value entirely, without any recursive merging.

Result for `merged_overwrite_config.json` (from example above):

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

## 3. Architecture

For a deep dive into the design principles, core components, and extensibility of the `JsonConfigMerger`, please refer to the [Architecture Documentation](docs/architecture_en.md).

## 4. Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to submit bug reports, feature requests, and code contributions.

## 5. License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
