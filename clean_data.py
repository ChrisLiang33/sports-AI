import json
import os
from datetime import datetime, timedelta

# Get yesterday's date
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%m-%d")

# File paths
odds_file_path = f'data/pregame/{yesterday_date}_pregame.json'  
scores_file_path = f'data/final_score/{yesterday_date}_final.json'  
output_file_path = f'data/training_data/{yesterday_date}_training.json'  

# Make sure the output directory exists
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

# Load the odds data
with open(odds_file_path, 'r') as odds_file:
    odds_data = json.load(odds_file)

# Load the scores data
with open(scores_file_path, 'r') as scores_file:
    scores_data = json.load(scores_file)

# Create a list to store combined data
combined_data = []

# Combine the data based on home and away teams
for odds in odds_data:
    home_team = odds['home_team']
    away_team = odds['away_team']

    # Find the corresponding score data for the same teams
    score_entry = next((score for score in scores_data if score['home_team'] == home_team and score['away_team'] == away_team), None)

    if score_entry:
        # Extract scores
        home_score = int(score_entry['scores'][0]['score'])
        away_score = int(score_entry['scores'][1]['score'])

        # Extract spreads
        home_spread = next(spread['spread'] for spread in odds['spread'] if spread['team'] == home_team)
        away_spread = next(spread['spread'] for spread in odds['spread'] if spread['team'] == away_team)

        if abs(home_score + home_spread - away_score) <= 2.5:  # Push
            home_covered = 'P'
            away_covered = 'P'
        elif home_score + home_spread + 8.5 < away_score:  
            home_covered = '-2'
            away_covered = '2'
        elif away_score + away_spread + 8.5 < home_score:
            home_covered = '2'
            away_covered = '-2'
        elif home_score + home_spread > away_score:  # Home team covered spread
            home_covered = '1'
            away_covered = '-1'
        elif away_score + away_spread > home_score:  # Away team covered spread
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
                {
                    'team': away_team,
                    'spread': away_spread
                },
                {
                    'team': home_team,
                    'spread': home_spread
                }
            ],
            'scores': score_entry['scores'],
            home_team: home_covered,
            away_team: away_covered,
        }
        combined_data.append(combined_entry)

# Save the combined data to the output file
with open(output_file_path, 'w') as output_file:
    json.dump(combined_data, output_file, indent=4)

print(f"Combined data with coverage information successfully saved to {output_file_path}.")
