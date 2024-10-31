import requests
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()
api_key = os.getenv("API_KEY")

print("System-level API Key:", os.environ.get("API_KEY"))

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
                    "spread": []  
                }
                for market in bookmaker.get("markets", []):
                    if market["key"] == "spreads":
                        for outcome in market.get("outcomes", []):
                            filtered_event["spread"].append({  
                                "team": outcome["name"],
                                "spread": outcome["point"], 
                            })

                if filtered_event["spread"]:
                    fanduel_odds.append(filtered_event)

    date_str = datetime.now().strftime("%m-%d")
    output_file_path = f'data/pregame/{date_str}_pregame.json'  

    with open(output_file_path, "w") as file:
        json.dump(fanduel_odds, file, indent=4)

    for key, value in response.headers.items():
        print(f"{key}: {value}")
    
    print(f"Data successfully written to {output_file_path} with {len(fanduel_odds)} entries.")
else:
    print(f"Error: {response.status_code} - {response.text}")
