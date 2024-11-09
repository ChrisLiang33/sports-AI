import csv
import os
from datetime import datetime
import firebase_admin
from firebase_admin import firestore, credentials

if not firebase_admin._apps:
    cred = credentials.Certificate("path/to/your-firebase-credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

NBA_TEAMS = [
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets",
    "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets",
    "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers",
    "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat",
    "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks",
    "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns",
    "Portland Trail Blazers", "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors",
    "Utah Jazz", "Washington Wizards"
]

def parse_recommendation(recommendation, home_team, away_team):
    if not recommendation or 'PASS' in recommendation.upper():
        return None
        
    if '(' in recommendation:
        return recommendation.split('(')[1].strip(')')
    
    if recommendation.upper() == 'HOME':
        return home_team
    elif recommendation.upper() == 'AWAY':
        return away_team
    return None

def process_predictions():
    today_date = datetime.now().strftime("%m-%d")
    doc_ref = db.collection('predictions').document(f'{today_date}_prediction')
    data = doc_ref.get()

    if not data.exists:
        print(f"{today_date} No prediction data available in Firestore.")
        return
    
    data = data.to_dict()
    date = data.get('date', today_date)

    games = data.get('games', {}).get('games', [])

    team_predictions = {team: 'DNP' for team in NBA_TEAMS}
    teams_playing = set()

    for game in games:
        if not isinstance(game, dict):
            print("Unexpected data format for a game entry:", game)
            continue

        matchup = game.get('matchup', {})
        home_team = matchup.get('home_team')
        away_team = matchup.get('away_team')

        if not home_team or not away_team:
            print("Invalid matchup data:", matchup)
            continue
        teams_playing.add(home_team)
        teams_playing.add(away_team)
        
        if 'prediction' in game and isinstance(game['prediction'], dict):
            recommendation = game['prediction'].get('recommendation', None)
            recommended_team = parse_recommendation(
                recommendation,
                home_team,
                away_team
            )
            if recommended_team:
                team_predictions[recommended_team] = '1'
                opponent = away_team if recommended_team == home_team else home_team
                team_predictions[opponent] = '0'
            else:
                team_predictions[home_team] = 'n/a'
                team_predictions[away_team] = 'n/a'
    
    csv_file_path = 'data/csv/live/prediction_tracking.csv'
    csv_data = {}
    header = ['Team']

    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            for row in reader:
                team_name = row[0]
                csv_data[team_name] = row[1:]

    if date not in header:
        header.append(date)
        for team in csv_data:
            csv_data[team].append('')

    for team in NBA_TEAMS:
        if team not in csv_data:
            csv_data[team] = [''] * (len(header) - 1) + [team_predictions[team]]
        else:
            csv_data[team][-1] = team_predictions[team]

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        sorted_teams = sorted(csv_data.keys())
        for team in sorted_teams:
            writer.writerow([team] + csv_data[team])

    print(f"CSV file '{csv_file_path}' updated successfully.")
    print(f"Teams with recommendations: {sum(1 for v in team_predictions.values() if v == '1')}")

async def main():
    process_predictions()
