from dotenv import load_dotenv
import os, json, requests
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import firestore, credentials

cred = credentials.Certificate("serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

load_dotenv()
api_key = os.getenv("API_KEY")
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%m-%d")
today_date = datetime.now().strftime("%m-%d")

async def get_final_score():
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
        # output_file_path = f'data/final_score/{yesterday_date}_final.json'
        # with open(output_file_path, "w") as file:
        #     json.dump(cleaned_data, file, indent=4)
        # print(f"Data successfully written to final.json file")

        doc_ref = db.collection('final_score').document(f'{yesterday_date}_finalScore')
        doc_ref.set({"games": cleaned_data})
        print(f"Data successfully written to Firestore")
    else:
        print(f"Error: {response.status_code} - {response.text}")

async def get_pregame_odds():
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
        
        # mannully input 
        # output_file_path = f'data/pregame/{date_str}_pregame.json'  
        # with open(output_file_path, "w") as file:
        #     json.dump(fanduel_odds, file, indent=4)
        # print(f"Data successfully written to {output_file_path}")

        doc_ref = db.collection('pregame_odds').document(f'{today_date}_pregame')
        doc_ref.set({"games": fanduel_odds})
    else:
        print(f"Error: {response.status_code} - {response.text}")

def normalize_team_name(name):
    return name.strip().lower()

async def form_trainingData():
    # odds_file_path = f'data/pregame/{yesterday_date}_pregame.json'  
    # scores_file_path = f'data/final_score/{yesterday_date}_final.json'  
    # output_file_path = f'data/training_data/{yesterday_date}_training.json' 

    try:
        doc_ref1 = db.collection('pregame_odds').document(f'{yesterday_date}_pregame')
        doc_ref2 = db.collection('final_score').document(f'{yesterday_date}_finalScore')

        odds_data_doc = doc_ref1.get()
        scores_data_doc = doc_ref2.get()

        if not odds_data_doc.exists:
            print(f"Pregame odds document for {yesterday_date} does not exist!")
        if not scores_data_doc.exists:
            print(f"Final score document for {yesterday_date} does not exist!")

        if odds_data_doc.exists and scores_data_doc.exists:
            odds_data = odds_data_doc.to_dict().get('games', [])
            scores_data = scores_data_doc.to_dict().get('games', [])
        else:
            print("One or both documents do not exist!")
            return
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    combined_data = []
    weight = 8.5
    super_weight = 15

    for odds in odds_data:
        home_team = normalize_team_name(odds['home_team'])
        away_team = normalize_team_name(odds['away_team'])

        score_entry = next((score for score in scores_data if 
                            normalize_team_name(score['home_team']) == home_team and 
                            normalize_team_name(score['away_team']) == away_team), None)

        # if score_entry is None:
        #     print(f"No score entry found for Home: '{home_team}', Away: '{away_team}'.")
        # else:
        #     print(f"Score Entry: {score_entry}")

        if score_entry:
            home_score = int(score_entry['scores'][0]['score'])
            away_score = int(score_entry['scores'][1]['score'])

            home_spread = next(spread['spread'] for spread in odds['spread'] if normalize_team_name(spread['team']) == home_team)
            away_spread = next(spread['spread'] for spread in odds['spread'] if normalize_team_name(spread['team']) == away_team)

            if abs(home_score + home_spread - away_score) <= 2.5:  
                home_covered = 'P'
                away_covered = 'P'
            elif home_score + home_spread + super_weight < away_score:  
                home_covered = '-3'
                away_covered = '3'
            elif away_score + away_spread + super_weight < home_score:
                home_covered = '3'
                away_covered = '-3'
            elif home_score + home_spread + weight < away_score:  
                home_covered = '-2'
                away_covered = '2'
            elif away_score + away_spread + weight < home_score:
                home_covered = '2'
                away_covered = '-2'
            elif home_score + home_spread > away_score:  
                home_covered = '1'
                away_covered = '-1'
            elif away_score + away_spread > home_score:
                home_covered = '-1'
                away_covered = '1'
            else:
                home_covered = 'n/a'
                away_covered = 'n/a'

            combined_entry = {
                'home_team': home_team,
                'away_team': away_team,
                'game_date': yesterday_date,
                'spread': [
                    {'team': away_team, 'spread': away_spread},
                    {'team': home_team, 'spread': home_spread}
                ],
                'scores': score_entry['scores'],
                home_team: home_covered,
                away_team: away_covered,
            }
            combined_data.append(combined_entry)

    # with open(output_file_path, 'w') as output_file:
    #     json.dump(combined_data, output_file, indent=4)
     
    doc_ref = db.collection('training_data').document(f'{yesterday_date}_trainingData')
    doc_ref.set({"games": combined_data})
    print(f"Data successfully written to Firestore")
