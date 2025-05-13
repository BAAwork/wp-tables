import os
import requests
import json
from datetime import datetime

# --- Настройки API ---
API_KEY = os.environ.get("RAPIDAPI_KEY")
API_HOST = "nhl-api5.p.rapidapi.com"
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST
}
OUTPUT_DIR = "output"
# Создаём папку output
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Функция для сохранения HTML ---
def save_html(filename: str, html_content: str):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Файл {path} создан.")

# --- 1. NHL Standings ---
resp = requests.get(
    "https://nhl-api5.p.rapidapi.com/nhlstandings",
    headers=HEADERS,
    params={"year": "2025"}
)
data_st = resp.json().get("standings", {}).get("entries", [])
# Сортировка по очкам
sorted_st = sorted(
    data_st,
    key=lambda e: int(next((s["displayValue"] for s in e.get("stats", []) if s.get("name") == "points"), "0")),
    reverse=True
)
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# Генерация таблицы Standings для TablePress
html_st = [
    '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; font-family: Arial; font-size:14px; width:100%;">',
    f'<caption style="caption-side: top; text-align:left; font-size:18px; font-weight:bold;">NHL Standings (Updated: {now})</caption>',
    '<thead><tr><th>RK</th><th>Team</th><th>GP</th><th>W</th><th>L</th><th>OTL</th><th>PTS</th><th>RW</th><th>PD</th><th>Avg Diff</th></tr></thead>',
    '<tbody>'
]
for idx, entry in enumerate(sorted_st, start=1):
    team = entry.get("team", {})
    team_name = team.get("displayName", "-")
    logo = team.get("logos", [{}])[0].get("href", "")
    stats = {s.get("name"): s.get("displayValue") for s in entry.get("stats", [])}
    html_st.append(
        '<tr>'
        f'<td>{idx}</td>'
        f'<td><img src="{logo}" style="height:20px;vertical-align:middle;"> {team_name}</td>'
        f'<td>{stats.get("gamesPlayed","-")}</td>'
        f'<td>{stats.get("wins","-")}</td>'
        f'<td>{stats.get("losses","-")}</td>'
        f'<td>{stats.get("otLosses","-")}</td>'
        f'<td>{stats.get("points","-")}</td>'
        f'<td>{stats.get("regWins","-")}</td>'
        f'<td>{stats.get("pointDifferential","-")}</td>'
        f'<td>{stats.get("differential","-")}</td>'
        '</tr>'
    )
html_st.append('</tbody></table>')
save_html("nhl_standings.html", "\n".join(html_st))

# --- 2. NHL Injuries ---
resp_inj = requests.get(
    "https://nhl-api5.p.rapidapi.com/injuries",
    headers=HEADERS
)
data_inj = resp_inj.json().get('injuries', [])
now2 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# Сбор всех травм в один TablePress-ready HTML
html_inj = [
    '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; font-family: Arial; font-size:14px; width:100%;">',
    f'<caption style="caption-side: top; text-align:left; font-size:18px; font-weight:bold;">NHL Injuries (Updated: {now2})</caption>',
    '<thead><tr><th>Team</th><th>Name</th><th>Position</th><th>Status</th><th>Reason</th><th>Est. Return Date</th></tr></thead>',
    '<tbody>'
]
for team_group in data_inj:
    team_name = team_group.get('displayName', 'Unknown')
    injuries = team_group.get('injuries', [])
    logo = ''
    if injuries:
        logo = injuries[0].get('athlete', {}).get('team', {}).get('logos', [{}])[0].get('href', '')
    for inj in injuries:
        ath = inj.get('athlete', {})
        name = ath.get('displayName') or f"{ath.get('firstName','')} {ath.get('lastName','')}".strip() or '-'
        pos = ath.get('position', {}).get('displayName', '-')
        status = inj.get('status', '-')
        reason = inj.get('details', {}).get('type') or inj.get('longComment') or inj.get('shortComment') or '-'
        ret = inj.get('details', {}).get('returnDate', '-')
        # Добавляем строку с колонкой Team
        html_inj.append(
            '<tr>'
            f'<td><img src="{logo}" style="height:20px;vertical-align:middle;"> {team_name}</td>'
            f'<td>{name}</td>'
            f'<td>{pos}</td>'
            f'<td>{status}</td>'
            f'<td>{reason}</td>'
            f'<td>{ret}</td>'
            '</tr>'
        )
html_inj.append('</tbody></table>')
save_html("nhl_injuries.html", "\n".join(html_inj))
