import json
import pandas as pd

# Load the first JSON file (scores)
with open('test2.json', 'r') as scores_file:
    scores_data = json.load(scores_file)

# Load the second JSON file (points)
with open('test1.json', 'r') as points_file:
    points_data = json.load(points_file)

# Create a dictionary to map team names to their respective points
points_dict = {}
for game in points_data:
    home_team = game['home_team']
    away_team = game['away_team']
    points_dict[(home_team, away_team)] = {
        'home_points': next(point['point'] for point in game['points'] if point['team'] == home_team),
        'away_points': next(point['point'] for point in game['points'] if point['team'] == away_team)
    }

# Combine data into a list
combined_data = []
for game in scores_data:
    home_team = game['home_team']
    away_team = game['away_team']
    if (home_team, away_team) in points_dict:
        home_score = int(game['scores'][0]['score'])
        away_score = int(game['scores'][1]['score'])
        home_point = points_dict[(home_team, away_team)]['home_points']
        away_point = points_dict[(home_team, away_team)]['away_points']

        # Check if each team covered the spread
        home_covered = 1 if (home_score - away_score) >= home_point else 0
        away_covered = 1 if (away_score - home_score) >= abs(away_point) else 0

        combined_data.append({
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'home_point': home_point,
            'away_point': away_point,
            'home_covered': home_covered,
            'away_covered': away_covered,
        })

# Create a DataFrame and save it to a CSV file
df = pd.DataFrame(combined_data)
df.to_csv('combined_data.csv', index=False)

print("Data successfully written to combined_data.csv")
