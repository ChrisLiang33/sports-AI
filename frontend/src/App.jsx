import { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/predictions")
      .then((response) => {
        setPredictions(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching predictions: ", error);
        setLoading(false);
      });
  }, []);
  if (loading) {
    return <div>Loading...</div>;
  }
  if (!predictions) {
    return <div>Error fetching predictions</div>;
  }

  return (
    <div>
      <h1>NBA Predictions</h1>
      <p>Date: {predictions.date}</p>
      <p>Analysis Timestamp: {predictions.analysis_timestamp}</p>

      <h2>Games:</h2>
      <ul>
        {predictions.games.map((game, index) => (
          <li key={index}>
            <h3>
              {game.matchup.away_team} vs {game.matchup.home_team}
            </h3>
            <p>Recommendation: {game.prediction.recommendation}</p>
            <p>Confidence: {game.prediction.confidence}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default App;
