from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config.json"
OUT = ROOT / "assets" / "dev-pulse.svg"


def load_config() -> dict:
    with CONFIG.open("r", encoding="utf-8") as f:
        return json.load(f)


def github_get(url: str, token: str | None = None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "sachith-dev-pulse",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read().decode("utf-8"))


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def human_age(delta_seconds: float) -> str:
    seconds = max(0, int(delta_seconds))
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def main() -> int:
    cfg = load_config()
    username = cfg["github_username"]
    token = os.getenv("GITHUB_TOKEN")

    now = datetime.now(timezone.utc)
    status = "OFFLINE"
    status_class = "offline"
    latest_repo = "No recent public activity"
    latest_event = "Waiting for activity"
    language = cfg.get("primary_stack", "JAVA")
    last_active = "unknown"

    try:
        events = github_get(f"https://api.github.com/users/{username}/events/public?per_page=30", token)
        if events:
            latest = events[0]
            created = parse_iso(latest["created_at"])
            age_minutes = (now - created).total_seconds() / 60
            last_active = human_age((now - created).total_seconds())
            latest_repo = latest.get("repo", {}).get("name", latest_repo).split("/")[-1]
            latest_event = latest.get("type", "GitHubEvent").replace("Event", "")

            if age_minutes <= cfg.get("active_minutes", 20):
                status = "ACTIVE NOW"
                status_class = "active"
            elif age_minutes <= cfg.get("recent_minutes", 180):
                status = "RECENTLY ACTIVE"
                status_class = "recent"
            elif age_minutes <= 1440:
                status = "IDLE"
                status_class = "idle"
            else:
                status = "OFFLINE"
                status_class = "offline"

            # Try to enrich with repo language.
            repo_full = latest.get("repo", {}).get("name")
            if repo_full:
                try:
                    repo = github_get(f"https://api.github.com/repos/{repo_full}", token)
                    language = repo.get("language") or language
                except Exception:
                    pass
    except Exception as exc:
        print(f"GitHub API fetch failed: {exc}", file=sys.stderr)
        status = "SYNC PENDING"
        status_class = "recent"
        latest_repo = "GitHub sync pending"
        latest_event = "FIRST RUN"
        last_active = "first run"

    colors = {
        "active": ("#2dfc9f", "#113c31"),
        "recent": ("#66e3ff", "#123442"),
        "idle": ("#ffd166", "#3c3212"),
        "offline": ("#9aa4b2", "#202632"),
    }
    accent, soft = colors[status_class]

    display_name = escape(cfg.get("display_name", username).upper())
    role = escape(cfg.get("role", "SOFTWARE ENGINEER"))
    language = escape(str(language).upper())
    latest_repo = escape(latest_repo)
    latest_event = escape(latest_event.upper())
    last_active = escape(last_active)
    status = escape(status)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="190" viewBox="0 0 920 190" role="img" aria-label="{display_name} GitHub developer activity status">
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#07111f"/>
      <stop offset="0.55" stop-color="#0a1727"/>
      <stop offset="1" stop-color="#08101b"/>
    </linearGradient>
    <linearGradient id="line" x1="0" x2="1">
      <stop offset="0" stop-color="#19d3ff" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#19d3ff" stop-opacity="0.85"/>
      <stop offset="1" stop-color="#19d3ff" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; }}
      .sans {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
      .muted {{ fill: #8fa1b5; }}
      .white {{ fill: #f5fbff; }}
    </style>
  </defs>

  <rect x="1" y="1" width="918" height="188" rx="22" fill="url(#bg)" stroke="#17324d"/>
  <rect x="18" y="18" width="884" height="154" rx="18" fill="#0a1422" fill-opacity="0.58" stroke="#14314a"/>

  <g transform="translate(42 39)">
    <text class="sans white" x="0" y="0" font-size="20" font-weight="800" letter-spacing="2">⚡ {display_name} DEV PULSE</text>
    <text class="mono muted" x="0" y="24" font-size="11" letter-spacing="1.2">{role}</text>
  </g>

  <g transform="translate(690 32)">
    <rect width="184" height="38" rx="19" fill="{soft}" stroke="{accent}" stroke-opacity="0.45"/>
    <circle cx="20" cy="19" r="6" fill="{accent}" filter="url(#glow)">
      <animate attributeName="r" values="5;8;5" dur="1.8s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="1;.65;1" dur="1.8s" repeatCount="indefinite"/>
    </circle>
    <text class="mono" x="36" y="24" font-size="12" font-weight="800" fill="{accent}">{status}</text>
  </g>

  <rect x="42" y="86" width="836" height="1" fill="url(#line)" opacity="0.75">
    <animate attributeName="opacity" values="0.3;1;0.3" dur="3s" repeatCount="indefinite"/>
  </rect>

  <g class="mono" transform="translate(42 112)" font-size="12">
    <text class="muted" x="0" y="0">STACK</text>
    <text class="white" x="0" y="20" font-size="15" font-weight="800">{language}</text>

    <text class="muted" x="188" y="0">LATEST REPO</text>
    <text class="white" x="188" y="20" font-size="15" font-weight="800">{latest_repo}</text>

    <text class="muted" x="492" y="0">ACTIVITY</text>
    <text class="white" x="492" y="20" font-size="15" font-weight="800">{latest_event}</text>

    <text class="muted" x="690" y="0">LAST ACTIVE</text>
    <text x="690" y="20" font-size="15" font-weight="800" fill="{accent}">{last_active}</text>
  </g>

  <text class="mono" x="42" y="164" font-size="9.5" fill="#50667c">AUTO-GENERATED FROM PUBLIC GITHUB ACTIVITY • REFRESHED BY GITHUB ACTIONS</text>
</svg>'''

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
