import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import HomePage from "./page/HomePage";
import RecapPage from "./page/RecapPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/recap" element={<RecapPage />} />
      </Routes>
    </Router>
  );
}

export default App;
