const Card = ({ away_team, home_team, pick, score, result }) => {
  const backgroundColor =
    result === true
      ? "bg-gradient-to-r from-green-400 to-green-600"
      : result === false
      ? "bg-gradient-to-r from-red-400 to-red-600"
      : "bg-gradient-to-r from-purple-500 to-blue-500";

  const away_logo = `/assets/${away_team}.png`;
  const home_logo = `/assets/${home_team}.png`;

  return (
    <div
      className={`card ${backgroundColor} shadow-md rounded-lg p-6 w-96 h-96 mx-auto border border-gray-200`}
    >
      <div className="flex items-center justify-center mb-2">
        <img
          src={away_logo}
          alt="Away Team Logo"
          className="max-w-full max-h-16 mr-2"
        />
        <span className="text-4xl text-white mx-4">VS</span>{" "}
        <img
          src={home_logo}
          alt="Home Team Logo"
          className="max-w-full max-h-16 ml-2"
        />
      </div>

      <div className="text-center text-lg font-semibold text-white mb-2">
        <div className="text-gray-200">{away_team}</div>
      </div>

      <div className="text-center text-lg font-semibold text-white mb-2">
        <div className="text-gray-200">{home_team}</div>
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
