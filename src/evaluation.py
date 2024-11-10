import pandas as pd
from datetime import datetime, timedelta
from firebase_admin import firestore
import numpy as np

db = firestore.client()

async def evaluate_predictions():
    main_df = pd.read_csv('/Users/chrisliang8/Desktop/sports-AI/data/csv/live/main.csv')
    prediction_df = pd.read_csv('/Users/chrisliang8/Desktop/sports-AI/data/csv/live/prediction_tracking.csv')

    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%m-%d")

    doc_ref = db.collection('predictions').document(f'{yesterday_date}_prediction')
    prediction_data = doc_ref.get()
    if not prediction_data.exists:
        print("No prediction data available for yesterday in Firestore.")
        return

    # Access the 'games' list within the nested prediction_data dictionary
    prediction_data = prediction_data.to_dict()
    games_data = prediction_data.get('games', {}).get('games', [])

    # Ensure we are working with a list of dictionaries
    if not isinstance(games_data, list):
        print(f"Unexpected data structure for 'games': {prediction_data} (Expected list of dictionaries)")
        return
    
    total_predictions = 0
    correct_predictions = 0
    incorrect_predictions = 0

    for idx, row in prediction_df.iterrows():
        team = row['Teams']
        prediction = row.get(yesterday_date, 'nan')

        if pd.notna(prediction) and str(prediction) == '1':
            team_performance = main_df.loc[main_df['Teams'] == team, yesterday_date].values
            
            if len(team_performance) > 0:
                performance_value = team_performance[0]
                
                if performance_value in ['p', 'P']:
                    performance_value = 1
                else:
                    if not np.isnan(performance_value):
                        performance_value = int(performance_value)
                total_predictions += 1
                is_correct = performance_value in ['0', '1', 'p', 'P', '2', '3', 1, 2, 3, -1]
                
                if is_correct:
                    correct_predictions += 1
                else:
                    incorrect_predictions += 1

                # Update the result in games_data
                for game in games_data:
                    if isinstance(game, dict):
                        matchup = game.get('matchup', {})
                        prediction = game.get('prediction', {})
                        away_team = matchup.get('away_team')
                        home_team = matchup.get('home_team')

                        if away_team and home_team and team in [away_team, home_team]:
                            prediction['result'] = is_correct
                            break
                    else:
                        print(f"Unexpected data type in game: {game} (Expected dictionary)")
                        
    doc_ref.set({"games": {"games": games_data}}, merge=True)  

    accuracy = (correct_predictions / total_predictions) * 100 if total_predictions else 0
    print(f"Accuracy: {accuracy}%")
    print(f"Total Predictions: {total_predictions}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Incorrect Predictions: {incorrect_predictions}")
