from __future__ import annotations

import argparse
import calendar
import json
import math
import os
import sys
import urllib.error
import urllib.request
from collections import OrderedDict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.json"
ASSETS = ROOT / "assets"
API = "https://api.github.com"
GRAPHQL = "https://api.github.com/graphql"


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def request_json(url: str, token: str | None = None, payload: dict | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "sachith-github-hud",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, headers=headers, data=data)
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.loads(res.read().decode("utf-8"))


def rest_get(path: str, token: str | None = None) -> Any:
    return request_json(f"{API}{path}", token)


def graphql(query: str, variables: dict[str, Any], token: str) -> Any:
    result = request_json(GRAPHQL, token, {"query": query, "variables": variables})
    if result.get("errors"):
        raise RuntimeError(result["errors"][0].get("message", "GitHub GraphQL error"))
    return result["data"]


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def compact_number(value: int) -> str:
    if value < 1000:
        return str(value)
    if value < 1_000_000:
        v = value / 1000
        return f"{v:.1f}K" if v < 10 else f"{v:.0f}K"
    v = value / 1_000_000
    return f"{v:.1f}M" if v < 10 else f"{v:.0f}M"


def truncate(text: str, limit: int) -> str:
    text = str(text)
    return text if len(text) <= limit else text[: max(0, limit - 1)] + "…"


def nice_axis(max_value: int) -> tuple[int, int]:
    max_value = max(20, max_value)
    rough_step = max_value / 4
    power = 10 ** math.floor(math.log10(rough_step))
    norm = rough_step / power
    if norm <= 1:
        nice = 1
    elif norm <= 2:
        nice = 2
    elif norm <= 5:
        nice = 5
    else:
        nice = 10
    step = int(nice * power)
    axis_max = int(math.ceil(max_value / step) * step)
    return axis_max, step


def fetch_repositories(username: str, token: str | None) -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = rest_get(
            f"/users/{username}/repos?type=owner&sort=updated&per_page=100&page={page}", token
        )
        if not isinstance(batch, list):
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        if page > 10:
            break
    return repos


def compute_streaks(day_counts: dict[date, int], today: date) -> tuple[int, int]:
    if not day_counts:
        return 0, 0


    cursor = today
    if day_counts.get(cursor, 0) == 0:
        cursor -= timedelta(days=1)
    current = 0
    while day_counts.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    best = 0
    run = 0
    for d in sorted(day_counts):
        if day_counts[d] > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return current, best


def month_buckets(day_counts: dict[date, int]) -> tuple[list[str], list[int]]:
    if not day_counts:
        return [], []
    buckets: "OrderedDict[tuple[int, int], int]" = OrderedDict()
    for d in sorted(day_counts):
        key = (d.year, d.month)
        buckets.setdefault(key, 0)
        buckets[key] += day_counts[d]
    labels = [calendar.month_abbr[m].upper() for (_, m) in buckets.keys()]
    values = list(buckets.values())
    return labels, values


def get_contributions(username: str, token: str | None) -> dict[str, Any]:
    if not token:
        raise RuntimeError("No token available for GraphQL contribution calendar")

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=364)
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays { date contributionCount }
            }
          }
        }
      }
    }
    """
    data = graphql(
        query,
        {
            "login": username,
            "from": start.isoformat().replace("+00:00", "Z"),
            "to": now.isoformat().replace("+00:00", "Z"),
        },
        token,
    )
    user = data.get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {username}")
    cal = user["contributionsCollection"]["contributionCalendar"]
    day_counts: dict[date, int] = {}
    for week in cal.get("weeks", []):
        for item in week.get("contributionDays", []):
            day_counts[date.fromisoformat(item["date"])] = int(item["contributionCount"])

    labels, values = month_buckets(day_counts)
    current, best = compute_streaks(day_counts, now.date())
    return {
        "total_contributions": int(cal.get("totalContributions", 0)),
        "current_streak": current,
        "best_streak": best,
        "month_labels": labels,
        "monthly_contributions": values,
    }


def resolve_username(cfg: dict[str, Any], cli_user: str | None = None) -> str:
    if cli_user and cli_user.strip():
        return cli_user.strip()

    env_owner = (os.getenv("GITHUB_REPOSITORY_OWNER") or os.getenv("TARGET_USER") or "").strip()
    config_user = str(cfg.get("github_username", "")).strip()

    
    if not config_user or config_user.upper() in ("AUTO", "YOUR_GITHUB_USERNAME", "USERNAME"):
        if env_owner:
            return env_owner

    
    if env_owner and env_owner.lower() != "sachith-gunarathna" and config_user.lower() == "sachith-gunarathna":
        return env_owner

    return config_user or env_owner or "Sachith-Gunarathna"


def resolve_display_name(cfg: dict[str, Any], username: str) -> str:
    name = str(cfg.get("display_name", "")).strip()
    if not name or name.upper() in ("AUTO", "YOUR_NAME", "DEV"):
        return username.upper()
    
    if username.lower() != "sachith-gunarathna" and name.upper() == "SACHITH":
        return username.upper()
    return name.upper()


def collect_data(cfg: dict[str, Any], force_demo: bool = False) -> dict[str, Any]:
    fallback = dict(cfg.get("fallback", {}))
    if force_demo:
        return fallback

    username = cfg["github_username"]
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    data = dict(fallback)

    user: dict[str, Any] = {}
    try:
        user = rest_get(f"/users/{username}", token)
        data["public_repos"] = int(user.get("public_repos", data.get("public_repos", 0)))
        data["followers"] = int(user.get("followers", data.get("followers", 0)))
    except Exception as exc:
        print(f"[warn] user API: {exc}", file=sys.stderr)

    repos: list[dict[str, Any]] = []
    try:
        repos = fetch_repositories(username, token)
        if repos:
            data["total_stars"] = sum(int(repo.get("stargazers_count", 0)) for repo in repos)
        elif repos is not None and user.get("public_repos", 0) == 0:
            data["total_stars"] = 0
    except Exception as exc:
        print(f"[warn] repos API: {exc}", file=sys.stderr)

    try:
        data.update(get_contributions(username, token))
    except Exception as exc:
        print(f"[warn] contributions API: {exc}", file=sys.stderr)

    now = datetime.now(timezone.utc)
    try:
        events = rest_get(f"/users/{username}/events/public?per_page=30", token)
        if events:
            latest = events[0]
            created = parse_iso(latest["created_at"])
            age_minutes = max(0, (now - created).total_seconds() / 60)
            repo_full = latest.get("repo", {}).get("name", "")
            latest_repo = repo_full.split("/")[-1] if repo_full else data.get("latest_repo", "WORKSPACE")
            data["latest_repo"] = latest_repo

            if age_minutes <= cfg.get("active_minutes", 20):
                data["status"] = "ACTIVE NOW"
            elif age_minutes <= cfg.get("recent_minutes", 180):
                data["status"] = "RECENTLY ACTIVE"
            elif age_minutes <= cfg.get("idle_minutes", 1440):
                data["status"] = "IDLE"
            else:
                data["status"] = "OFFLINE"

            if repo_full:
                repo_obj = next((r for r in repos if r.get("full_name") == repo_full), None)
                if repo_obj and repo_obj.get("language"):
                    data["latest_language"] = repo_obj["language"]
                else:
                    try:
                        repo_data = rest_get(f"/repos/{repo_full}", token)
                        if repo_data.get("language"):
                            data["latest_language"] = repo_data["language"]
                    except Exception:
                        pass
        else:
            data["status"] = "IDLE"
            if repos:
                data["latest_repo"] = repos[0].get("name", "WORKSPACE")
                data["latest_language"] = repos[0].get("language") or cfg.get("primary_stack", "JAVA")
    except Exception as exc:
        print(f"[warn] public events API: {exc}", file=sys.stderr)

    return data


def theme(mode: str) -> dict[str, str]:
    if mode == "dark":
        return {
            "bg": "#061018",
            "panel": "#081821",
            "panel2": "#07151d",
            "text": "#F4FAFC",
            "muted": "#91B8C8",
            "grid": "#123441",
            "border": "#1B8FA5",
            "cyan": "#53E9F0",
            "teal": "#30E2C2",
            "gold": "#FFD365",
            "pink": "#FF6685",
            "blue": "#5BD8F5",
            "area": "#0FA8A8",
        }
    return {
        "bg": "#F8FCFD",
        "panel": "#FFFFFF",
        "panel2": "#FBFEFF",
        "text": "#102130",
        "muted": "#597B96",
        "grid": "#D7F2F6",
        "border": "#46C7D7",
        "cyan": "#20C5D3",
        "teal": "#28D9BE",
        "gold": "#F3C85C",
        "pink": "#F25F7B",
        "blue": "#48BFE3",
        "area": "#7EE3E8",
    }


def defs(t: dict[str, str], prefix: str) -> str:
    return f"""
  <defs>
    <pattern id="{prefix}-grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="{t['grid']}" stroke-width="1"/>
    </pattern>
    <linearGradient id="{prefix}-area" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="{t['area']}" stop-opacity=".45"/>
      <stop offset="1" stop-color="{t['area']}" stop-opacity=".04"/>
    </linearGradient>
    <filter id="{prefix}-glow" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace; }}
      .title {{ font-weight: 800; letter-spacing: 3px; }}
      .label {{ font-size: 17px; letter-spacing: 1.7px; }}
      .value {{ font-weight: 800; }}
    </style>
  </defs>"""


def frame(t: dict[str, str]) -> str:
    c = t["border"]
    return f"""
  <rect x="1" y="1" width="2046" height="606" fill="none" stroke="{c}" stroke-width="2"/>
  <path d="M1 38L38 1 M2010 1L2047 38 M1 570L38 607 M2010 607L2047 570" fill="none" stroke="{c}" stroke-width="2"/>"""


def render_system_metrics(cfg: dict[str, Any], data: dict[str, Any], mode: str) -> str:
    t = theme(mode)
    values = [
        ("PUBLIC REPOS", str(data.get("public_repos", 0)), t["teal"]),
        ("TOTAL STARS", str(data.get("total_stars", 0)), t["gold"]),
        ("FOLLOWERS", str(data.get("followers", 0)), t["pink"]),
        ("365D SIGNALS", compact_number(int(data.get("total_contributions", 0))), t["blue"]),
    ]
    cards = []
    x0, gap, w, y, h = 50, 28, 473, 280, 170
    for i, (label, value, accent) in enumerate(values):
        x = x0 + i * (w + gap)
        bx = x + w - 105
        cards.append(f"""
  <g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{t['panel2']}" stroke="{t['border']}" stroke-opacity=".55"/>
    <rect x="{x}" y="{y}" width="{w}" height="8" fill="{accent}"/>
    <text class="mono label" x="{x+32}" y="{y+56}" fill="{t['muted']}">{escape(label)}</text>
    <text class="mono value" x="{x+32}" y="{y+126}" font-size="54" fill="{t['text']}">{escape(value)}</text>
    <rect x="{bx}" y="{y+105}" width="18" height="20" fill="{accent}" opacity=".75"/>
    <rect x="{bx+34}" y="{y+83}" width="18" height="42" fill="{accent}" opacity=".85"/>
    <rect x="{bx+68}" y="{y+60}" width="18" height="65" fill="{accent}"/>
  </g>""")

    primary = escape(str(cfg.get("primary_stack", "JAVA")).upper())
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="608" viewBox="0 0 2048 608" role="img" aria-label="GitHub system metrics">
{defs(t, 'metrics')}
  <rect width="2048" height="608" fill="{t['bg']}"/>
  <rect width="2048" height="608" fill="url(#metrics-grid)" opacity=".62"/>
{frame(t)}
  <rect x="50" y="170" width="1948" height="86" fill="{t['panel']}" stroke="{t['border']}" stroke-width="1.5"/>
  <rect x="50" y="170" width="16" height="86" fill="{t['cyan']}"/>
  <text class="mono title" x="98" y="225" font-size="36" fill="{t['text']}">GITHUB // SYSTEM METRICS</text>
  <text class="mono" x="1760" y="220" font-size="24" fill="{t['muted']}">PRIMARY:</text>
  <text class="mono value" x="1965" y="220" font-size="24" text-anchor="end" fill="{t['teal']}">{primary}</text>
{''.join(cards)}
  <text class="mono" x="52" y="500" font-size="16" fill="{t['muted']}">PUBLIC PROFILE TELEMETRY // CACHED SERVER-SIDE // NO CLIENT TOKEN EXPOSED</text>
</svg>"""


def render_contribution(cfg: dict[str, Any], data: dict[str, Any], mode: str) -> str:
    t = theme(mode)
    labels = list(data.get("month_labels") or [])
    values = [int(v) for v in (data.get("monthly_contributions") or [])]
    if not labels or not values:
        labels = list(cfg.get("fallback", {}).get("month_labels", []))
        values = list(cfg.get("fallback", {}).get("monthly_contributions", []))
    n = min(len(labels), len(values))
    labels, values = labels[:n], values[:n]
    if n < 2:
        labels, values = ["NOW", "NOW"], [0, 1]
        n = 2

    chart_left, chart_top, chart_w, chart_h = 120, 225, 1850, 245
    axis_max, step = nice_axis(max(values))
    points: list[tuple[float, float]] = []
    for i, v in enumerate(values):
        x = chart_left + (chart_w * i / (n - 1))
        y = chart_top + chart_h - (chart_h * v / axis_max)
        points.append((x, y))
    line_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area_points = f"{points[0][0]:.1f},{chart_top+chart_h} {line_points} {points[-1][0]:.1f},{chart_top+chart_h}"

    x_grid = []
    x_labels = []
    dots = []
    for i, ((x, y), lab) in enumerate(zip(points, labels)):
        x_grid.append(f'<line x1="{x:.1f}" y1="{chart_top}" x2="{x:.1f}" y2="{chart_top+chart_h}" stroke="{t["border"]}" stroke-opacity=".45" stroke-dasharray="7 8"/>')
        x_labels.append(f'<text class="mono" x="{x:.1f}" y="508" text-anchor="middle" font-size="18" fill="{t["muted"]}">{escape(str(lab).upper())}</text>')
        accent = t["pink"] if i == n - 1 else t["cyan"]
        filt = ' filter="url(#contrib-glow)"' if i == n - 1 else ""
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{t["panel"]}" stroke="{accent}" stroke-width="3"{filt}/>' )

    y_grid = []
    y_labels = []
    for k in range(5):
        val = step * k
        if k == 4:
            val = axis_max
        y = chart_top + chart_h - chart_h * (val / axis_max)
        y_grid.append(f'<line x1="{chart_left}" y1="{y:.1f}" x2="{chart_left+chart_w}" y2="{y:.1f}" stroke="{t["border"]}" stroke-opacity=".45" stroke-dasharray="7 8"/>')
        y_labels.append(f'<text class="mono" x="94" y="{y+6:.1f}" text-anchor="end" font-size="17" fill="{t["muted"]}">{val}</text>')

    total = compact_number(int(data.get("total_contributions", 0)))
    current = str(data.get("current_streak", 0)) + "D"
    best = str(data.get("best_streak", 0)) + "D"
    username = escape(str(cfg.get("github_username", "GITHUB")).upper())

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="608" viewBox="0 0 2048 608" role="img" aria-label="GitHub contribution signal graph">
{defs(t, 'contrib')}
  <rect width="2048" height="608" fill="{t['bg']}"/>
  <rect width="2048" height="608" fill="url(#contrib-grid)" opacity=".56"/>
{frame(t)}
  <rect x="50" y="108" width="1948" height="78" fill="{t['panel']}" stroke="{t['border']}" stroke-width="1.5"/>
  <rect x="50" y="108" width="16" height="78" fill="{t['cyan']}"/>
  <text class="mono title" x="98" y="158" font-size="34" fill="{t['text']}">CONTRIBUTION // SIGNAL GRAPH</text>
  <line x1="1765" y1="128" x2="1765" y2="163" stroke="{t['border']}" stroke-width="3"/>
  <text class="mono" x="1980" y="157" text-anchor="end" font-size="22" fill="{t['muted']}">LAST 365 DAYS</text>
  {''.join(y_grid)}
  {''.join(x_grid)}
  <line x1="{chart_left}" y1="{chart_top+chart_h}" x2="{chart_left+chart_w}" y2="{chart_top+chart_h}" stroke="{t['muted']}" stroke-width="1.5"/>
  <line x1="{chart_left}" y1="{chart_top}" x2="{chart_left}" y2="{chart_top+chart_h}" stroke="{t['muted']}" stroke-width="1.5"/>
  {''.join(y_labels)}
  <polygon points="{area_points}" fill="url(#contrib-area)"/>
  <polyline points="{line_points}" fill="none" stroke="{t['cyan']}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>
  {''.join(dots)}
  {''.join(x_labels)}
  <rect x="48" y="535" width="1952" height="58" fill="{t['panel']}" stroke="{t['border']}"/>
  <text class="mono" x="80" y="572" font-size="18" fill="{t['muted']}">TOTAL</text>
  <text class="mono value" x="165" y="572" font-size="24" fill="{t['teal']}">{escape(total)}</text>
  <line x1="375" y1="549" x2="375" y2="580" stroke="{t['border']}" stroke-width="2"/>
  <text class="mono" x="438" y="572" font-size="18" fill="{t['muted']}">CURRENT STREAK</text>
  <text class="mono value" x="650" y="572" font-size="24" fill="{t['gold']}">{escape(current)}</text>
  <line x1="860" y1="549" x2="860" y2="580" stroke="{t['border']}" stroke-width="2"/>
  <text class="mono" x="945" y="572" font-size="18" fill="{t['muted']}">BEST STREAK</text>
  <text class="mono value" x="1118" y="572" font-size="24" fill="{t['pink']}">{escape(best)}</text>
  <line x1="1518" y1="549" x2="1518" y2="580" stroke="{t['border']}" stroke-width="2"/>
  <text class="mono" x="1968" y="572" text-anchor="end" font-size="17" fill="{t['muted']}">{username} // GITHUB</text>
</svg>"""


def status_style(status: str, t: dict[str, str]) -> tuple[str, str]:
    s = status.upper()
    if "ACTIVE NOW" in s:
        return "CODING NOW", t["teal"]
    if "RECENT" in s:
        return "RECENT ACTIVITY", t["blue"]
    if "IDLE" in s:
        return "IDLE", t["gold"]
    if "OFFLINE" in s:
        return "OFFLINE", t["muted"]
    return "SYNC PENDING", t["blue"]


def render_dev_signal(cfg: dict[str, Any], data: dict[str, Any], mode: str) -> str:
    t = theme(mode)
    display = escape(str(cfg.get("display_name", cfg.get("github_username", "DEV"))).upper())
    lang = escape(str(data.get("latest_language") or cfg.get("primary_stack", "JAVA")).upper())
    ide = escape(str(cfg.get("active_ide", "INTELLIJ IDEA")).upper())
    if cfg.get("project_mode", "latest_repo") == "fixed":
        project = str(cfg.get("project_name", "FULL-STACK WORKSPACE"))
    else:
        project = str(data.get("latest_repo") or cfg.get("project_name", "FULL-STACK WORKSPACE"))
    project = escape(truncate(project.upper().replace("_", " "), 28))
    raw_status = str(data.get("status", "SYNC PENDING")).upper()
    badge, badge_color = status_style(raw_status, t)
    last_signal = escape(truncate(raw_status, 18))
    footer = " // ".join(str(x).upper() for x in cfg.get("footer_tools", []))
    footer = escape(truncate(footer, 86))

    cards = [
        ("LANGUAGE", lang, t["gold"], 48, 455),
        ("ACTIVE IDE", ide, t["teal"], 535, 1005),
        ("PROJECT", project, t["pink"], 1038, 1585),
        ("LAST SIGNAL", last_signal, t["blue"], 1618, 1998),
    ]
    card_svg = []
    for label, value, accent, x1, x2 in cards:
        w = x2 - x1
        font = 38 if w > 450 else 34
        if len(value) > 22:
            font = 31
        card_svg.append(f"""
  <g>
    <rect x="{x1}" y="312" width="{w}" height="158" fill="{t['panel2']}" stroke="{t['border']}"/>
    <path d="M{x1} 332v-18h20 M{x2-20} 312h20v20 M{x1} 450v18h20 M{x2-20} 470h20v-20" fill="none" stroke="{t['border']}"/>
    <rect x="{x1+24}" y="336" width="18" height="18" fill="{accent}"/>
    <text class="mono label" x="{x1+58}" y="353" fill="{t['muted']}">{escape(label)}</text>
    <text class="mono value" x="{x1+44}" y="417" font-size="{font}" fill="{t['text']}">{value}</text>
    <rect x="{x1+44}" y="440" width="{max(130, w-145)}" height="7" fill="{accent}"/>
  </g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="608" viewBox="0 0 2048 608" role="img" aria-label="Developer signal status">
{defs(t, 'dev')}
  <rect width="2048" height="608" fill="{t['bg']}"/>
  <rect width="2048" height="608" fill="url(#dev-grid)" opacity=".62"/>
{frame(t)}
  <rect x="48" y="185" width="1952" height="96" fill="{t['panel']}" stroke="{t['border']}"/>
  <rect x="48" y="185" width="16" height="96" fill="{t['cyan']}"/>
  <text class="mono title" x="94" y="231" font-size="34" fill="{t['text']}">{display} // DEV SIGNAL</text>
  <text class="mono" x="95" y="260" font-size="18" letter-spacing="2" fill="{t['muted']}">LOCAL IDE HEARTBEAT • PIXEL HUD v3</text>
  <rect x="1400" y="199" width="342" height="67" fill="{t['panel2']}" stroke="{badge_color}"/>
  <path d="M1400 214v-15h18 M1724 199h18v15 M1400 251v15h18 M1724 266h18v-15" fill="none" stroke="{badge_color}"/>
  <rect x="1427" y="220" width="22" height="22" fill="{badge_color}"/>
  <text class="mono value" x="1471" y="241" font-size="22" fill="{badge_color}">{escape(badge)}</text>
  <rect x="1790" y="234" width="18" height="28" fill="{t['gold']}"/>
  <rect x="1820" y="216" width="18" height="46" fill="{t['gold']}" opacity=".85"/>
  <rect x="1850" y="194" width="18" height="68" fill="{t['teal']}"/>
  <rect x="1880" y="220" width="18" height="42" fill="{t['cyan']}"/>
  <rect x="1910" y="202" width="18" height="60" fill="{t['pink']}"/>
  <rect x="1940" y="224" width="18" height="38" fill="{t['pink']}" opacity=".85"/>
  {''.join(card_svg)}
  <text class="mono" x="70" y="525" font-size="16" fill="{t['muted']}">{footer}</text>
  <text class="mono" x="1980" y="525" text-anchor="end" font-size="16" fill="{t['muted']}">SYS.{display}</text>
</svg>"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"generated {path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate GitHub HUD status bars")
    parser.add_argument("--demo", action="store_true", help="Use fallback data from config.json")
    parser.add_argument("--user", type=str, default=None, help="GitHub username override")
    args = parser.parse_args()

    cfg = load_config()
    username = resolve_username(cfg, args.user)
    display_name = resolve_display_name(cfg, username)
    cfg["github_username"] = username
    cfg["display_name"] = display_name
    print(f"[info] Generating status bars for user: {username} (display: {display_name})")

    data = collect_data(cfg, force_demo=args.demo)
    ASSETS.mkdir(parents=True, exist_ok=True)

    for mode in ("dark", "light"):
        write(ASSETS / f"system-metrics-{mode}.svg", render_system_metrics(cfg, data, mode))
        write(ASSETS / f"contribution-signal-{mode}.svg", render_contribution(cfg, data, mode))
        write(ASSETS / f"dev-signal-{mode}.svg", render_dev_signal(cfg, data, mode))

    write(ASSETS / "data.json", json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
