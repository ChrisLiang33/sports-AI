const Card = ({ away_team, home_team, pick, score, result }) => {
  const backgroundColor =
    result === true
      ? "bg-green-500"
      : result === false
      ? "bg-red-500"
      : "bg-gradient-to-r from-purple-500 to-blue-500";

  return (
    <div
      className={`card ${backgroundColor} shadow-md rounded-lg p-6 max-w-xs h-72 mx-auto border border-gray-200`}
    >
      <div className="team1 text-lg font-semibold text-white mb-2">
        <span className="text-gray-200">Away Team:</span> {away_team}
      </div>
      <div className="team2 text-lg font-semibold text-white mb-2">
        <span className="text-gray-200">Home Team:</span> {home_team}
      </div>
      <div className="pick text-md text-yellow-300 font-medium mb-4">
        <span className="text-gray-200">Recommendation:</span> {pick}
      </div>
      <div className="score text-md text-green-300 font-medium mb-4">
        <span className="text-gray-200">Confidence:</span> {score}
      </div>
      <div className="result text-md text-white font-medium">
        <span className="text-gray-200">Result:</span>{" "}
        {result === true ? "Win" : result === false ? "Lost" : "Pending"}
      </div>
    </div>
  );
};

export default Card;
