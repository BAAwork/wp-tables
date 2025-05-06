import os
import requests
import json

# 1) Ensure the API key is set in the environment
APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "44ddd738e030e35c6c99a180eb490a65")
if not APIFOOTBALL_KEY:
    raise RuntimeError("Please set the APIFOOTBALL_KEY environment variable")

# 2) Fetch teams for League 38, Season 2023
url = "https://v3.football.api-sports.io/teams"
headers = {"x-apisports-key": APIFOOTBALL_KEY}
params = {"league": "38", "season": "2023"}
resp = requests.get(url, headers=headers, params=params)
resp.raise_for_status()

teams = resp.json().get("response", [])

# 3) Build HTML fragment including team logos and prepare JSON table
rows = []
json_table = []
for entry in teams:
    team = entry["team"]
    venue = entry["venue"]
    logo_url = team.get("logo", "")
    # HTML row
    rows.append(
        "<tr>"
        f"<td><img src='{logo_url}' alt='{team['name']} logo' width='50'></td>"
        f"<td>{team.get('name', '')}</td>"
        f"<td>{team.get('code', '')}</td>"
        f"<td>{team.get('country', '')}</td>"
        f"<td>{team.get('founded', '')}</td>"
        f"<td>{venue.get('name', '')}</td>"
        "</tr>"
    )
    # JSON entry
    json_table.append({
        "logo": logo_url,
        "name": team.get("name", ""),
        "code": team.get("code", ""),
        "country": team.get("country", ""),
        "founded": team.get("founded", ""),
        "venue": venue.get("name", "")
    })

rows_html = "\n    ".join(rows)

html_fragment = f"""
<table border="1" cellpadding="4" cellspacing="0">
  <thead>
    <tr>
      <th>Logo</th><th>Name</th><th>Code</th><th>Country</th><th>Founded</th><th>Venue</th>
    </tr>
  </thead>
  <tbody>
    {rows_html}
  </tbody>
</table>
"""

# 4) Write to fragment.html
output_html = "fragment.html"
with open(output_html, "w", encoding="utf-8") as f:
    f.write("<html><head><meta charset='utf-8'><title>Teams with Logos</title></head><body>\n")
    f.write(html_fragment)
    f.write("\n</body></html>")

print(f"✅ HTML fragment with logos written to {output_html}. Open it in your browser to view.")

# 5) Write JSON table to fragment.json
output_json = "fragment.json"
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(json_table, f, ensure_ascii=False, indent=2)

print(f"✅ JSON table written to {output_json}.")
