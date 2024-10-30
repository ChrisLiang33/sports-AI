import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

api_key = os.getenv("API_KEY")
url = 'https://api.the-odds-api.com/v4/sports/basketball_nba/odds/'

params = {
    'apiKey': api_key,
    'markets': 'spreads',
    'regions': 'us',
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    
    fanduel_odds = []
    for event in data:
        for bookmaker in event.get("bookmakers", []):
            if bookmaker["key"] == "fanduel":
                filtered_event = {
                    "home_team": event["home_team"],
                    "away_team": event["away_team"],
                    "points": []  
                }

                for market in bookmaker.get("markets", []):
                    if market["key"] == "spreads":
                        for outcome in market.get("outcomes", []):
                            filtered_event["points"].append({
                                "team": outcome["name"],
                                "point": outcome["point"],
                            })

                if filtered_event["points"]:
                    fanduel_odds.append(filtered_event)

    with open("odds_data.json", "w") as file:
        json.dump(fanduel_odds, file, indent=4)

    for key, value in response.headers.items():
        print(f"{key}: {value}")

    print(f"Data successfully written to odds_data.json with {len(fanduel_odds)} entries.")
else:
    print(f"Error: {response.status_code} - {response.text}")
