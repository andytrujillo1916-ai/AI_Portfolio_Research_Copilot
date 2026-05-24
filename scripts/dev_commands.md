# Developer Commands (Windows-Friendly)

This project uses PowerShell helper scripts instead of a Makefile.

## Install Requirements

```powershell
pip install -r requirements.txt
```

## Run App

```powershell
.\scripts\run_app.ps1
```

## Run Tests

```powershell
.\scripts\run_tests.ps1
```

## Freeze Requirements

```powershell
pip freeze > requirements.txt
```

## Git Status

```powershell
git status
```

## Commit Checklist

1. Run app and confirm Streamlit loads.
2. Run tests and confirm they pass.
3. Review changed files: `git status` and `git diff`.
4. Confirm research-only boundaries remain intact.
5. Commit with a clear message.
