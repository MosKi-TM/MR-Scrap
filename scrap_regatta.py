from bs4 import BeautifulSoup
import requests
import json

url = "https://www.matchracingresults.com"  # Replace with the actual URL
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

results_div = soup.find("div", id="results")
events = []

for li in results_div.find_all("li"):
    flag = li.find("img")["src"]
    country = li.find("img")["title"]
    link = li.find("a")["href"]
    title = li.find("a").text
    text = li.get_text(strip=True)
    date_and_location = text.replace(title, "").strip(", ")

    events.append({
        "title": title,
        "link": url+link,
    })


with open("matchracing_events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)
