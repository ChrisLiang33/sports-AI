import pandas as pd
from datetime import datetime, timedelta
import json
from firebase_admin import firestore

db = firestore.client()

async def evaluate_predictions():
    main_df = pd.read_csv('/Users/chrisliang8/Desktop/sports-AI/data/csv/live/main.csv')
    prediction_df = pd.read_csv('/Users/chrisliang8/Desktop/sports-AI/data/csv/live/prediction_tracking.csv')

    yesterday_date = main_df.columns[-1]

    total_predictions = 0
    correct_predictions = 0
    incorrect_predictions = 0
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%m-%d")
    doc_ref = db.collection('prediction').document(f'{yesterday_date}_prediction')
    prediction_data = doc_ref.get()
    if not prediction_data.exists:
        print("No yesterday prediction data available")
        return
    prediction_data = prediction_data.to_dict().get('games', [])

    for idx, row in prediction_df.iterrows():
        team = row['Teams']
        prediction = row[yesterday_date]
        if prediction != 'nan' and prediction == 1:
            team_performance = main_df.loc[main_df['Teams'] == team, yesterday_date].values
            if len(team_performance) > 0:
                if team_performance[0] == 'p' or team_performance[0] == 'P':
                    team_performance = 1
                else:
                    team_performance = int(team_performance[0])
                total_predictions += 1
                is_correct = team_performance in ['0', '1', 'p', 'P', '2', '3', 1, 2, 3, -1]
                if is_correct:
                    correct_predictions += 1
                else:
                    incorrect_predictions += 1
                for game in prediction_data["games"]:
                        if team in [game["matchup"]["away_team"], game["matchup"]["home_team"]]:
                            game["prediction"]["result"] = is_correct
                            break

    accuracy = (correct_predictions / total_predictions) * 100 if total_predictions else 0
    doc_ref = db.collection('predictions').document(f'{yesterday_date}_prediction')
    doc_ref.set({"games": prediction_data})
    print(f'updated {yesterday_date} predictions with win/loss results')
        
    # results_dict = {
    #     'Date': [yesterday_date],
    #     'Total_Predictions': [total_predictions],
    #     'Correct_Predictions': [correct_predictions],
    #     'Incorrect_Predictions': [incorrect_predictions],
    #     'Accuracy': [accuracy]
    # }

    # results_df = pd.DataFrame(results_dict)

    # results_path = '/Users/chrisliang8/Desktop/sports-AI/data/csv/live/results.csv'
    # try:
    #     existing_results = pd.read_csv(results_path)
    #     updated_results = pd.concat([existing_results, results_df], ignore_index=True)
    # except FileNotFoundError:
    #     updated_results = results_df

    # updated_results.to_csv(results_path, index=False)

    print(f"Accuracy: {accuracy}%")
    print(f"Total Predictions: {total_predictions}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Incorrect Predictions: {incorrect_predictions}")
