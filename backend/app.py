from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
   CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TeamMetrics(BaseModel):
  recent_performance: float
  score: float

class Spreads(BaseModel):
  actual_spread: float

class Prediction(BaseModel):
    recommendation: str
    confidence: float
    result: Optional[bool] = None

class Matchup(BaseModel):
    away_team: str
    home_team: str

class Game(BaseModel):
    matchup: Matchup
    spreads: Spreads
    team_metrics: Dict[str, TeamMetrics]
    prediction: Prediction

class PredictionResponse(BaseModel):
    date: str
    analysis_timestamp: str
    games: List[Game]
  
@app.get('/predictions', response_model=PredictionResponse)
async def get_predictions():
   todays_date = datetime.now().strftime('%m-%d')
   with open(f'../data/prediction/{todays_date}_prediction.json', 'r') as f:
      data = json.load(f)
   return data

@app.get('/yesterday_predictions', response_model=PredictionResponse)
async def get_yesterday_predictions():
    yesterdays_date = (datetime.now() - timedelta(days=1)).strftime('%m-%d')
    with open(f'../data/prediction/{yesterdays_date}_prediction.json', 'r') as f:
        data = json.load(f)
    return data



