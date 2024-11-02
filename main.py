import asyncio
from src.get_pregame_odds import get_pregame_odds
from src.get_final_score import get_final_score
from src.clean_data import clean_data
from src.compile_data import compile_data
from src.model import model_main
from src.prediction_into_csv import main as prediction_into_csv
from src.evaluation import evaluate_predictions

async def main():
    try:
        print("Starting the process...")
        
        print("Getting pregame odds...")
        await get_pregame_odds()
        
        print("Getting final scores...")
        await get_final_score()
        
        print("Cleaning data...")
        await clean_data()
        
        print("Compiling data...")
        await compile_data()

        print('making predictions')
        await model_main()

        print("Updating CSV file...")
        await prediction_into_csv()

        print('yesterdays results ')
        await evaluate_predictions()

        print("Process completed successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
