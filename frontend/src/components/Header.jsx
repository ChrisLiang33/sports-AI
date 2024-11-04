import React from "react";

const Header = ({ predictions }) => {
  return (
    <div className="bg-blue-800 text-white py-4 px-6 shadow-lg">
      <h1 className="text-3xl font-bold">NBA Predictions</h1>
      <p className="text-sm mt-1">Date: {predictions.date}</p>
    </div>
  );
};

export default Header;
