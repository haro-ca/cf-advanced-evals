# Agent Instructions

## Package Management

**This project uses `uv` exclusively for package management and execution.**

### Installing Dependencies
- Use `uv add <package>` to install packages
- DO NOT use `pip install`

### Running Python Code
- Use `uv run <script.py>` to execute Python files
- Use `uv run python -m <module>` for module execution
- DO NOT use `python` directly

### Examples
```bash
# Install a package
uv add requests

# Run a script
uv run main.py

# Run a module
uv run python -m pytest
```
