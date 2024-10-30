import json
import pandas as pd

# Load the scores and points from your JSON files
with open('test1.json', 'r') as points_file:
    points_data = json.load(points_file)

with open('test2.json', 'r') as scores_file:
    scores_data = json.load(scores_file)

# Create a dictionary to store point spreads for quick access
points_dict = {}
for game in points_data:
    home_team = game['home_team']
    away_team = game['away_team']
    points_dict[(home_team, away_team)] = {
        'home_points': next(point['point'] for point in game['points'] if point['team'] == home_team),
        'away_points': next(point['point'] for point in game['points'] if point['team'] == away_team)
    }

combined_data = []
for game in scores_data:
    home_team = game['home_team']
    away_team = game['away_team']
    
    if (home_team, away_team) in points_dict:
        home_score = int(game['scores'][0]['score'])
        away_score = int(game['scores'][1]['score'])
        home_point = points_dict[(home_team, away_team)]['home_points']
        away_point = points_dict[(home_team, away_team)]['away_points']

        # Print statements to trace the values
        print(f"Processing game: {home_team} vs {away_team}")
        print(f"Scores -> {home_team}: {home_score}, {away_team}: {away_score}")
        print(f"Point Spread -> {home_team}: {home_point}, {away_team}: {away_point}")

        # Determine if each team covered the spread using the revised logic
        home_covered = 1 if (home_score - away_score) + home_point >= 0 else 0
        away_covered = 1 if (away_score - home_score) - abs(away_point) >= 0 else 0

        # Print coverage results
        print(f"{home_team} covered: {home_covered}, {away_team} covered: {away_covered}")

        # Append results for both teams with team, score, covered
        combined_data.append({'team': home_team, 'score': home_score, 'covered': home_covered})
        combined_data.append({'team': away_team, 'score': away_score, 'covered': away_covered})

# Create a DataFrame and save it to a CSV file
df = pd.DataFrame(combined_data)
df.to_csv('combined_data.csv', index=False)

print("Data successfully written to combined_data.csv")
