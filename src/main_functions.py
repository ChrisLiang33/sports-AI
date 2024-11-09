from dotenv import load_dotenv
import os, requests, csv
from datetime import datetime, timedelta, timezone
import firebase_admin
from firebase_admin import firestore, credentials
from collections import defaultdict
import pandas as pd

load_dotenv()
cred = credentials.Certificate("/Users/chrisliang8/Desktop/sports-AI/serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

api_key = os.getenv("API_KEY")
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%m-%d")
today_date = datetime.now().strftime("%m-%d")

#use sports odds api to get yesterday final scores and write to firebase
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

        doc_ref = db.collection('final_score').document(f'{yesterday_date}_finalScore')
        doc_ref.set({"games": cleaned_data})
        print(f"final score successfully written to db")
    else:
        print(f"Error: {response.status_code} - {response.text}")

#use sports odds api to get pregame odds and write to firebase
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
        odds = []
        for event in data:
            iso_date = event.get('commence_time')
            utc_time = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
            est_offset = timedelta(hours=-5)
            est_time = utc_time.replace(tzinfo=timezone.utc).astimezone(timezone(est_offset))
            formatted_date = est_time.strftime("%m-%d")
            if formatted_date != today_date:
                continue
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
                        odds.append(filtered_event)
        
        doc_ref = db.collection('pregame_odds').document(f'{today_date}_pregame')
        doc_ref.set({"games": odds})
        print(f"pregame odds successfully written to db")
    else:
        print(f"Error: {response.status_code} - {response.text}")

#this function takes yesterday's pregame odds and yesterdays final scores and determines the rating, combines them as training data and writes to db

# write to csv 
async def form_trainingData():
    try:
        doc_ref1 = db.collection('pregame_odds').document(f'{yesterday_date}_pregame')
        doc_ref2 = db.collection('final_score').document(f'{yesterday_date}_finalScore')
        odds_data_doc = doc_ref1.get()
        scores_data_doc = doc_ref2.get()
        if not odds_data_doc.exists:
            print(f"Pregame odds document for {yesterday_date} does not exist!")
            return
        if not scores_data_doc.exists:
            print(f"Final score document for {yesterday_date} does not exist!")
            return
        odds_data = odds_data_doc.to_dict().get('games', [])
        scores_data = scores_data_doc.to_dict().get('games', [])
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    combined_data = []
    weight = 8.5
    super_weight = 15

    for odds in odds_data:
        home_team = (odds['home_team'])
        away_team = (odds['away_team'])
        score_entry = next((score for score in scores_data if 
                            (score['home_team']) == home_team and 
                            (score['away_team']) == away_team), None)
        if score_entry:
            home_score = int(score_entry['scores'][0]['score'])
            away_score = int(score_entry['scores'][1]['score'])
            home_spread = next(spread['spread'] for spread in odds['spread'] if (spread['team']) == home_team)
            away_spread = next(spread['spread'] for spread in odds['spread'] if (spread['team']) == away_team)

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
     
    doc_ref = db.collection('training_data').document(f'{yesterday_date}_trainingData')
    doc_ref.set({"games": combined_data})
    print(f"trainingData successfully written to db")

    data = combined_data
    team_coverage = defaultdict(lambda: defaultdict(str))

    for game in data:
        game_date = game['game_date']
        for team in [game['home_team'], game['away_team']]:
            coverage = game[team]
            team_coverage[team][game_date] = coverage  

    csv_file_path = 'data/csv/live/main.csv'
    csv_data = {}

    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as csvfile:
            existing_data = list(csv.reader(csvfile))
            header = existing_data[0]
            existing_dates = header[1:]  

            for row in existing_data[1:]:
                team_name = row[0]
                csv_data[team_name] = row[1:]

    if yesterday_date not in existing_dates:
        header.append(yesterday_date)  
        for team in csv_data:
            csv_data[team].append('')

    for team in team_coverage:
        if team not in csv_data:
            csv_data[team] = [''] * len(existing_dates)
            csv_data[team].append(team_coverage[team][yesterday_date])
        else:
            csv_data[team][-1] = team_coverage[team][yesterday_date] 

    csv_data_rows = []
    for team, ratings in csv_data.items():
        csv_data_rows.append([team] + ratings)

    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header)
        csv_writer.writerows(csv_data_rows)

    print(f"main CSV updated successfully.")


    #write to db
    df = pd.read_csv(csv_file_path)
    collection_ref = db.collection('main')
    data_to_write = df.reset_index().to_dict(orient='records')
    for data in data_to_write:
        team_name = data['Teams']
        collection_ref.document(team_name).set(data)
    print("Data written to Firestore successfully.")

    # read from db
    docs = collection_ref.get()
    if len(docs) == 0:
        print("No documents found in Firestore.")
    else:
        print(f"Found {len(docs)} documents in Firestore.")
        firebase_data = []
        for doc in docs:
            firebase_data.append(doc.to_dict())
    
        df_from_firebase = pd.DataFrame(firebase_data)
        if 'Teams' not in df_from_firebase.columns:
            print("Error: 'Teams' column not found in Firebase data.")
            print("Firebase Data Columns: ", df_from_firebase.columns)
        else:
            if 'index' in df_from_firebase.columns:
                df_from_firebase = df_from_firebase.drop(columns=['index'])
            df = df.set_index('Teams')
            df_from_firebase = df_from_firebase.set_index('Teams')
            df = df.sort_index()
            df_from_firebase = df_from_firebase.sort_index()
            df = df.reindex(sorted(df.columns), axis=1)
            df_from_firebase = df_from_firebase.reindex(sorted(df_from_firebase.columns), axis=1)
            df_cleaned = df.fillna("").astype(str)
            df_from_firebase_cleaned = df_from_firebase.fillna("").astype(str)

            if df_cleaned.equals(df_from_firebase_cleaned):
                print("Data matches between CSV and Firebase.")
            else:
                print("Data mismatch between CSV and Firebase.")
                print("CSV Data:\n", df.head())
                print("Firebase Data:\n", df_from_firebase.head())