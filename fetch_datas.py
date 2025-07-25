import requests
from bs4 import BeautifulSoup
import json
import os
import re
import unicodedata

def normalize_name(name):
    if not name:
        return ""
    name = unicodedata.normalize('NFKD', name)
    return ''.join(c for c in name if not unicodedata.combining(c)).lower().strip()


def sanitize_filename(name):
    # Replace any character that is not alphanumeric, space, hyphen, or underscore with underscore
    return re.sub(r'[^\w\s-]', '_', name).strip().replace(' ', '_')


def fetch_match(regattas_name, url):
    k=True
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    all_matches = []

    for table in soup.find_all("table"):
        # Skip tables without any result cells
        if not table.find("td", class_="result"):
            continue

        headers = table.find_all("th", class_="result")
        skippers = [th.get("title") for th in headers if th.get("title")]
        rows = table.find_all("tr")[1:]  # skip header row
        
        if len(skippers) > 2:
            
            seen_matches = set()

            for row in rows:
                
                skipper_cell = row.find("td", class_="skipper")
                if not skipper_cell:
                    continue
                row_skipper = normalize_name(skipper_cell.text.strip())
                result_cells = row.find_all("td", class_="result")
                offset = 0
                for i, cell in enumerate(result_cells):
                    if normalize_name(skippers[i]) == row_skipper:
                        offset = 1

                    if not cell.text.strip() or normalize_name(skippers[i+offset]) == row_skipper:
                        continue

                    opponent = normalize_name(skippers[i+offset])
                    match_key = tuple(sorted([row_skipper, opponent]))
                    if match_key in seen_matches:
                        continue
                    seen_matches.add(match_key)

                    result = cell.text.strip()
                    winner = row_skipper if result == "1" else opponent
                    loser = opponent if result == "1" else row_skipper
                    all_matches.append({
                        "regatta": regattas_name,
                        "phase": table.get("id") or "round-robin",
                        "winner": winner,
                        "loser": loser,
                        "match": f"{row_skipper} vs {opponent}",
                        "race": 0
                    })

        else:
            # Head-to-Head Table
            rows = table.find_all("tr")
            skipper_cells = table.find_all("td", class_="skipper")
            if len(skipper_cells) == 2:
                s1 = normalize_name(skipper_cells[0].text.strip())
                s2 = normalize_name(skipper_cells[1].text.strip())

                s1_results = [td.text.strip() for td in rows[1].find_all("td", class_="result") if td.text.strip() != ""]
                s2_results = [str(abs(int(x)-1)) if x.isdigit() else "1" for x in s1_results]
                for i in range(len(s1_results)):
                    if not s1_results[i] or not s2_results[i]:
                        continue
                    if s1_results[i] == "1":
                        winner, loser = s1, s2
                    else:
                        winner, loser = s2, s1
                    all_matches.append({
                        "regatta": regattas_name,
                        "phase": table.get("id") or "knockout",
                        "winner": winner,
                        "loser": loser,
                        "match": f"{s1} vs {s2}",
                        "race": i + 1
                    })

    # Save results to JSON file
    with open(f"output/{sanitize_filename(regattas_name)}.json", "w", encoding="utf-8") as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=2)

    return all_matches

with open("matchracing_events.json", "r", encoding="utf-8") as f:
    events = json.load(f)


all_event_matches = []
for event in events:
    matches = fetch_match(event["title"], event["link"])
    all_event_matches.extend(matches)


with open("all_match_results.json", "w", encoding="utf-8") as f:
    json.dump(all_event_matches, f, ensure_ascii=False, indent=2)
