from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("../serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

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
    # date: str
    # analysis_timestamp: str
    games: List[Game]
  
todays_date = datetime.now().strftime('%m-%d')
yesterdays_date = (datetime.now() - timedelta(days=1)).strftime('%m-%d')

@app.get('/predictions', response_model=PredictionResponse)
async def get_predictions():
    doc_ref = db.collection('predictions').document(f'{todays_date}_prediction')
    pregame_data = doc_ref.get()
    if not pregame_data.exists:
        return {"message": "No pregame available"}
    pregame_data = pregame_data.to_dict().get('games', [])
    return pregame_data

@app.get('/yesterday_predictions', response_model=PredictionResponse)
async def get_yesterday_predictions():
    doc_ref = db.collection('predictions').document(f'{yesterdays_date}_prediction')
    pregame_data = doc_ref.get()
    if not pregame_data.exists:
        return {"message": "No pregame available"}
    pregame_data = pregame_data.to_dict().get('games', [])
    return pregame_data

