# SACHITH GitHub HUD

Code-generated GitHub profile status bars with matching **light + dark** versions.

This folder generates all 6 SVG files from one Python script:

- `assets/system-metrics-dark.svg`
- `assets/system-metrics-light.svg`
- `assets/contribution-signal-dark.svg`
- `assets/contribution-signal-light.svg`
- `assets/dev-signal-dark.svg`
- `assets/dev-signal-light.svg`

## What updates automatically

**System Metrics**
- Public repositories
- Total stars across public repositories
- Followers
- Last-365-day GitHub contributions

**Contribution Signal**
- Contribution total
- Current streak
- Best streak
- Month-by-month graph for the last 365 days

**Dev Signal**
- Latest public repository/project
- Latest repository language
- Activity state (`ACTIVE NOW`, `RECENTLY ACTIVE`, `IDLE`, `OFFLINE`)
- IDE name comes from `config.json` because GitHub cannot detect your local IDE

## 1. Put the folder in your GitHub profile repo

For this setup the profile repository is expected to be:

```text
Sachith-Gunarathna/Sachith-Gunarathna
```

Copy the included files/folders into that repo and push them to `main`.

## 2. Optional: add a PAT for the contribution calendar

The workflow first tries `GH_PAT` and otherwise uses the automatic `GITHUB_TOKEN`.

If GitHub Actions reports a GraphQL permission error, create a classic personal access token with public read access and add it to:

```text
Repository Settings → Secrets and variables → Actions → New repository secret
Name: GH_PAT
```

Do **not** put the token inside `config.json`, the Python file, or README.

## 3. Run it once

Open:

```text
Actions → Update GitHub HUD → Run workflow
```

The workflow regenerates the SVGs and commits only when something actually changes.

## 4. Add the bars to your profile README

Use the snippets from `README_SNIPPET.md`.

## Local preview

No third-party Python packages are required.

Generate demo/fallback data without internet:

```bash
python scripts/generate_status.py --demo
```

Generate live data when a GitHub token is available:

```bash
GH_TOKEN=your_token python scripts/generate_status.py
```

On Windows PowerShell:

```powershell
$env:GH_TOKEN="your_token"
python scripts/generate_status.py
```

## Customize

Edit only `config.json` for normal customization.

- `display_name`: heading name
- `primary_stack`: primary language shown in System Metrics
- `active_ide`: IDE shown in Dev Signal
- `project_mode`: `latest_repo` or `fixed`
- `project_name`: used when project mode is `fixed` and as a fallback
- activity thresholds can also be changed there

The `fallback` section is used only when live GitHub data cannot be fetched or when `--demo` is used.
