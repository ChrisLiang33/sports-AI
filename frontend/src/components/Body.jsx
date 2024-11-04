import React, { useState } from "react";
import Card from "./Card";
import Sidebar from "./Sidebar";

const Body = ({ predictions }) => {
  const [sortedGames, setSortedGames] = useState(predictions.games);
  const [isAscending, setIsAscending] = useState(true);

  const sortGamesByConfidence = () => {
    const sorted = [...sortedGames].sort((a, b) =>
      isAscending
        ? a.prediction.confidence - b.prediction.confidence
        : b.prediction.confidence - a.prediction.confidence
    );
    setSortedGames(sorted);
    setIsAscending(!isAscending);
  };

  return (
    <div className="px-6 py-8 bg-gradient-to-b from-purple-600 to-blue-500 min-h-screen flex">
      <Sidebar />

      <div className="flex-1">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-semibold text-gray-100">Games:</h2>
          <button
            onClick={sortGamesByConfidence}
            className="bg-blue-600 text-white px-4 py-2 rounded-md shadow hover:bg-blue-700"
          >
            Sort by Confidence {isAscending ? "↑" : "↓"}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedGames.map((game, index) => (
            <Card
              key={index}
              away_team={game.matchup.away_team}
              home_team={game.matchup.home_team}
              score={game.prediction.confidence}
              pick={game.prediction.recommendation}
              result={game.prediction.result}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Body;
