import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

api_key = os.getenv("API_KEY")
url = 'https://api.the-odds-api.com/v4/sports/basketball_nba/scores/'

params = {
    'apiKey': api_key,
    'daysFrom': 1,  
    'dateFormat': 'iso' 
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    
    cleaned_data = []
    for game in data:
        if game.get("scores") is not None:
            valid_scores = [score for score in game["scores"] if score["score"] is not None]

            if valid_scores:
                cleaned_game = {
                    "home_team": game["home_team"],
                    "away_team": game["away_team"],
                    "scores": valid_scores
                }
                cleaned_data.append(cleaned_game)
                
    with open("scores_data.json", "w") as file:
        json.dump(cleaned_data, file, indent=4)

    print(f"Data successfully written to scores_data.json with {len(cleaned_data)} entries.")
else:
    print(f"Error: {response.status_code} - {response.text}")