import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from datetime import datetime, timedelta
from firebase_admin import firestore
import pandas as pd
import numpy as np
# this file is a model that will be used to predict the outcome of NBA games based on the spread. The model will use past rating data from the csv file and pregame data to make predictions. The model will calculate metrics for each team and analyze the matchup to make a recommendation. The model will print the analysis results and save the results to a json file.

db = firestore.client()

def load_and_prepare_data(csv_content, pregame_content):
    try:
        lines = [line.strip() for line in csv_content.split('\n') if line.strip()]
        headers = lines[0].split(',')
        data = [line.split(',') for line in lines[1:]]
        df = pd.DataFrame(data, columns=headers)
        df.set_index(headers[0], inplace=True)
        value_map = {
            '3': 3.0,
            '-3': -3.0,
            '2': 2.0,
            '-2': -2.0,
            '1': 1.0,
            '-1': -1.0,
            'P': 0.5,
            'p': 0.5,
            '': np.nan
        }
        for col in df.columns:
            df[col] = df[col].map(value_map)
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise

def calculate_metrics(df):
    metrics = {}
    for team in df.index:
        team_data = df.loc[team]
        last_3 = team_data.dropna()[-3:]
        recent_performance = last_3.mean() if len(last_3) > 0 else 0
        overall_performance = team_data.dropna().mean()
        volatility = team_data.dropna().std()
        consistency = 1 / (1 + volatility) if not pd.isna(volatility) else 0
        metrics[team] = {
            'recent_performance': recent_performance,
            'overall_performance': overall_performance,
            'volatility': volatility,
            'consistency': consistency
        }
    return metrics

def analyze_matchup(home_team, away_team, metrics, spread):
    home_metrics = metrics.get(home_team, {})
    away_metrics = metrics.get(away_team, {})
    if not home_metrics or not away_metrics:
        return None
    home_score = (
        home_metrics['recent_performance'] * 0.5 +
        home_metrics['overall_performance'] * 0.3 +
        home_metrics['consistency'] * 0.2
    )
    away_score = (
        away_metrics['recent_performance'] * 0.5 +
        away_metrics['overall_performance'] * 0.3 +
        away_metrics['consistency'] * 0.2
    )
    spread_value = home_score - away_score
    actual_spread = spread
    spread_difference = spread_value - (actual_spread / 10)
    if spread_difference > 0.3:
        recommendation = f"HOME ({home_team})"
        recommended_team = home_team
    elif spread_difference < -0.3:
        recommendation = f"AWAY ({away_team})"
        recommended_team = away_team
    else:
        recommendation = "PASS"
        recommended_team = None
    return {
        'home_team': home_team,
        'away_team': away_team,
        'home_score': round(home_score, 3),
        'away_score': round(away_score, 3),
        'actual_spread': actual_spread,
        'recommendation': recommendation,
        'recommended_team': recommended_team,
        'confidence': round(abs(spread_difference) * 2, 2),  # Scale confidence
        'volatility_warning': home_metrics['volatility'] > 1.5 or away_metrics['volatility'] > 1.5,
        'home_recent_games': metrics[home_team]['recent_performance'],
        'away_recent_games': metrics[away_team]['recent_performance']
    }

def analyze_todays_games(csv_data, pregame_data):
    df = load_and_prepare_data(csv_data, pregame_data)
    metrics = calculate_metrics(df)
    results = []
    for game in pregame_data:
        home_team = game['home_team']
        away_team = game['away_team']
        home_spread = next((s['spread'] for s in game['spread'] if s['team'] == home_team), 0)
        analysis = analyze_matchup(home_team, away_team, metrics, home_spread)
        if analysis:
            results.append(analysis)
    return results

def print_analysis(results):
    print("\nNBA Spread Analysis Results:")
    print("=" * 80)
    for result in results:
        print(f"\n{result['away_team']} @ {result['home_team']}")
        print(f"Current Spread: {result['actual_spread']} (home team)")
        print(f"Recent Performance (Last 3 games):")
        print(f"  {result['home_team']}: {result['home_recent_games']:.2f}")
        print(f"  {result['away_team']}: {result['away_recent_games']:.2f}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Confidence: {result['confidence']:.2f}")
        if result['volatility_warning']:
            print("⚠️ WARNING: High volatility detected")
        print("-" * 80)

async def model_main():
    with open('data/csv/live/main.csv', 'r') as file:
        csv_data = file.read()
    today_date = datetime.now().strftime("%m-%d")
    doc_ref = db.collection('pregame_odds').document(f'{today_date}_pregame')
    pregame_data = doc_ref.get()
    if not pregame_data.exists:
        print("No pregame data available")
        return
    pregame_data = pregame_data.to_dict().get('games', [])

    results = analyze_todays_games(csv_data, pregame_data)
    prediction_results = {
        "games": []
    }
    for result in results:
        game_result = {
            "matchup": {
                "away_team": result['away_team'],
                "home_team": result['home_team']
            },
            "spreads": {
                "actual_spread": float(result['actual_spread']),
            },
            "team_metrics": {
                "home": {
                    "recent_performance": float(result['home_recent_games']),
                    "score": float(result['home_score'])
                },
                "away": {
                    "recent_performance": float(result['away_recent_games']),
                    "score": float(result['away_score'])
                }
            },
            "prediction": {
                "recommendation": result['recommendation'],
                "confidence": float(result['confidence']),
            }
        }
        prediction_results["games"].append(game_result)
    doc_ref = db.collection('predictions').document(f'{today_date}_prediction')
    doc_ref.set({"games": prediction_results})
    # print_analysis(results)
    print(f"prediction_result saved to Firestore")