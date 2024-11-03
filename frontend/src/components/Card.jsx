const Card = ({ away_team, home_team, pick, score }) => {
  return (
    <div className="card bg-white shadow-md rounded-lg p-6 max-w-sm mx-auto border border-gray-200">
      <div className="team1 text-lg font-semibold text-gray-700 mb-2">
        <span className="text-gray-500">Away Team:</span> {away_team}
      </div>
      <div className="team2 text-lg font-semibold text-gray-700 mb-2">
        <span className="text-gray-500">Home Team:</span> {home_team}
      </div>
      <div className="pick text-md text-blue-600 font-medium mb-4">
        <span className="text-gray-500">Recommendation:</span> {pick}
      </div>
      <div className="score text-md text-green-600 font-medium">
        <span className="text-gray-500">Confidence:</span> {score}
      </div>
    </div>
  );
};

export default Card;
