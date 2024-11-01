import pandas as pd
import numpy as np
import json
from datetime import datetime

def load_and_prepare_data(csv_content, pregame_content):
    try:
        # Create DataFrame from CSV content
        lines = [line.strip() for line in csv_content.split('\n') if line.strip()]
        
        # Parse the header and data
        headers = lines[0].split(',')
        data = [line.split(',') for line in lines[1:]]
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        df.set_index(headers[0], inplace=True)
        
        # Convert string values to numeric
        value_map = {
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
        
        # Last 3 games performance (excluding NaN)
        last_3 = team_data.dropna()[-3:]
        recent_performance = last_3.mean() if len(last_3) > 0 else 0
        
        # Overall performance
        overall_performance = team_data.dropna().mean()
        
        # Volatility (standard deviation)
        volatility = team_data.dropna().std()
        
        # Consistency score (inverse of volatility, normalized)
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
    
    # Calculate advantage scores
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
    
    # Adjust for home court advantage
    home_score += 0.2
    
    # Calculate spread value
    spread_value = home_score - away_score
    
    # Compare to actual spread
    actual_spread = spread
    spread_difference = spread_value - (actual_spread / 10)  # Normalize spread
    
    # Determine recommendation with team name
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
        'model_spread_value': round(spread_value * 10, 1),  # Convert back to points
        'actual_spread': actual_spread,
        'recommendation': recommendation,
        'recommended_team': recommended_team,
        'confidence': round(abs(spread_difference) * 2, 2),  # Scale confidence
        'volatility_warning': home_metrics['volatility'] > 1.5 or away_metrics['volatility'] > 1.5,
        'home_recent_games': metrics[home_team]['recent_performance'],
        'away_recent_games': metrics[away_team]['recent_performance']
    }

def analyze_todays_games(csv_data, pregame_data):
    # Load and prepare data
    df = load_and_prepare_data(csv_data, pregame_data)
    metrics = calculate_metrics(df)
    
    results = []
    for game in pregame_data:
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Find the spread for home team
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
        print(f"Model Spread Value: {result['model_spread_value']}")
        print(f"Recent Performance (Last 3 games):")
        print(f"  {result['home_team']}: {result['home_recent_games']:.2f}")
        print(f"  {result['away_team']}: {result['away_recent_games']:.2f}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Confidence: {result['confidence']:.2f}")
        if result['volatility_warning']:
            print("⚠️ WARNING: High volatility detected")
        print("-" * 80)

# Example usage
if __name__ == "__main__":
    with open('data/csv/main.csv', 'r') as file:
        csv_data = file.read()
    
    today_date = datetime.now().strftime("%m-%d")
    pregame_path = f'data/pregame/{today_date}_pregame.json'  
    with open(pregame_path, 'r') as file:
        pregame_data = json.load(file)
    
    results = analyze_todays_games(csv_data, pregame_data)
    print_analysis(results)