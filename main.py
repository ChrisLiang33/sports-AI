import asyncio
from src.main_functions import get_pregame_odds, get_final_score, form_trainingData
from src.make_predictions import model_main
from src.prediction_into_csv import main as prediction_into_csv
from src.evaluation import evaluate_predictions

async def main():
    try:
        print("Getting pregame odds...")
        await get_pregame_odds()
        
        print("Getting final scores...")
        await get_final_score()
        
        print("getting training data...")
        await form_trainingData()

        print('making predictions')
        await model_main()

        print("Updating prediction CSV file...")
        await prediction_into_csv()

        print('yesterdays results ')
        await evaluate_predictions()

        print("Process completed successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
