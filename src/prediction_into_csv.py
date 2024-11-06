import json
import csv
import os
from datetime import datetime
from collections import defaultdict

# prediction to prediction csv 
# this file saves the predictions from the prediction.json file to the prediction_tracking.csv file

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

def process_predictions(json_file_path):
    """
    Process JSON predictions file and update CSV tracking file.
    Uses:
    - '1' for recommended team
    - '0' for opponent of recommended team
    - 'n/a' for teams not playing or in PASS games
    """
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    date = data['date']
    games = data['games']
    
    team_predictions = {team: 'DNP' for team in NBA_TEAMS}
    
    teams_playing = set()
    
    for game in games:
        home_team = game['matchup']['home_team']
        away_team = game['matchup']['away_team']
        
        teams_playing.add(home_team)
        teams_playing.add(away_team)
        
        if 'prediction' in game:
            recommended_team = parse_recommendation(
                game['prediction']['recommendation'],
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
    
    if os.path.exists(csv_file_path):
        backup_path = f'data/csv/backup/prediction_tracking_backup_{date}.csv'
        with open(csv_file_path, 'r') as existing_file:
            existing_data = existing_file.readlines()
        with open(backup_path, 'w') as backup_file:
            backup_file.writelines(existing_data)
    
    csv_data = {}
    header = ['Team']
    
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            for row in reader:
                team_name = row[0]
                csv_data[team_name] = row[1:]
    
    if date not in header[1:]:
        header.append(date)
        for team in csv_data:
            csv_data[team].append('')
    
    for team in NBA_TEAMS:
        if team not in csv_data:
            csv_data[team] = [''] * (len(header) - 2) + [team_predictions[team]]
        else:
            csv_data[team][-1] = team_predictions[team]
    
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        sorted_teams = sorted(csv_data.keys())
        for team in sorted_teams:
            writer.writerow([team] + csv_data[team])

    print(f"CSV file '{csv_file_path}' updated successfully.")
    print(f"Processed predictions for {date}")
    print(f"Teams playing today: {len(teams_playing)}")
    print(f"Teams with recommendations: {sum(1 for v in team_predictions.values() if v == '1')}")

async def main():
    today_date = datetime.now().strftime("%m-%d")
    json_file_path = f"data/prediction/{today_date}_prediction.json"
    process_predictions(json_file_path)