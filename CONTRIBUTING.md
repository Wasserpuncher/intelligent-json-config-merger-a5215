# Contributing to Intelligent JSON Config Merger

We welcome contributions to the Intelligent JSON Config Merger project! Whether it's reporting bugs, suggesting new features, or submitting code, your help is invaluable. Please take a moment to review this document to understand how to contribute effectively.

## Table of Contents

1.  [Code of Conduct](#code-of-conduct)
2.  [How to Report Bugs](#how-to-report-bugs)
3.  [How to Suggest Features](#how-to-suggest-features)
4.  [Your First Code Contribution](#your-first-code-contribution)
5.  [Setting Up Your Development Environment](#setting-up-your-development-environment)
6.  [Coding Guidelines](#coding-guidelines)
7.  [Submitting Changes](#submitting-changes)
8.  [License](#license)

## 1. Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md) (if applicable, otherwise state a simple rule like 'be respectful'). By participating, you are expected to uphold this code. Please report unacceptable behavior to [project maintainer email/method].

## 2. How to Report Bugs

If you find a bug, please open an issue on our [GitHub Issues page](https://github.com/your-username/intelligent-json-config-merger/issues).

When reporting a bug, please include:

*   A clear and concise description of the bug.
*   Steps to reproduce the behavior.
*   Expected behavior.
*   Actual behavior.
*   Screenshots or code snippets if helpful.
*   Your operating system, Python version, and any other relevant environment details.

## 3. How to Suggest Features

We love new ideas! If you have a feature request, please open an issue on our [GitHub Issues page](https://github.com/your-username/intelligent-json-config-merger/issues).

When suggesting a feature, please include:

*   A clear and concise description of the proposed feature.
*   Why this feature would be useful.
*   Any potential challenges or alternative solutions you've considered.

## 4. Your First Code Contribution

New to open source or this project? We recommend looking for issues labeled `good first issue` or `help wanted`.

If you plan to contribute code, it's always a good idea to discuss your proposed changes in an issue first, especially for larger features, to ensure it aligns with the project's direction.

## 5. Setting Up Your Development Environment

1.  **Fork the repository**: Click the "Fork" button at the top right of the [GitHub repository](https://github.com/your-username/intelligent-json-config-merger).
2.  **Clone your fork**: 
    ```bash
    git clone https://github.com/YOUR_USERNAME/intelligent-json-config-merger.git
    cd intelligent-json-config-merger
    ```
3.  **Create a virtual environment**: 
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
4.  **Install dependencies**: 
    ```bash
    pip install -r requirements.txt
    ```

## 6. Coding Guidelines

*   **Python Style**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for code style. We use `flake8` for linting.
*   **Type Hinting**: Use Python's [type hints](https://docs.python.org/3/library/typing.html) for clarity and maintainability.
*   **Docstrings**: All public classes, methods, and functions should have clear, concise docstrings following [PEP 257](https://www.python.org/dev/peps/pep-0257/). Docstrings should be in English.
*   **Comments**: Use inline comments (`#`) to explain complex logic or non-obvious parts of the code. **Inline comments must be in German** to aid beginners and fulfill the bilingual requirement.
*   **Variable Names**: Use descriptive English variable and function names (e.g., `merge_strategy`, `base_config`).
*   **Tests**: All new features or bug fixes should be accompanied by unit tests in `test_main.py` using the `unittest` framework. Ensure existing tests pass.

## 7. Submitting Changes

1.  **Create a new branch**: 
    ```bash
    git checkout -b feature/your-feature-name-or-bugfix/issue-number
    ```
2.  **Make your changes**: Implement your feature or fix the bug.
3.  **Run tests**: 
    ```bash
    pytest
    ```
    Ensure all tests pass.
4.  **Run linting**: 
    ```bash
    flake8 .
    ```
    Address any linting issues.
5.  **Commit your changes**: Write clear, concise commit messages. A good commit message explains *what* changed and *why*.
    ```bash
    git commit -m "feat: Add support for XYZ feature" 
    # or 
    git commit -m "fix: Resolve bug in ABC functionality"
    ```
6.  **Push your branch**: 
    ```bash
    git push origin feature/your-feature-name-or-bugfix/issue-number
    ```
7.  **Open a Pull Request (PR)**: Go to your fork on GitHub and click the "New pull request" button. Provide a clear description of your changes, reference any related issues, and ensure all checks (CI/CD) pass.

## 8. License

By contributing to Intelligent JSON Config Merger, you agree that your contributions will be licensed under the [MIT License](LICENSE) of this project.
