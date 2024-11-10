import { useState, useEffect } from "react";
import axios from "axios";
import "../index.css";
import Header from "../components/Header";
import Footer from "../components/Footer";
import Body from "../components/Body";
import LoadingPage from "./LoadingPage";

const HomePage = () => {
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(true);
  web = "https://sports-ai.onrender.com";
  local = "http://127.0.0.1:8000";
  useEffect(() => {
    axios
      .get(`${web}/predictions`)
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
    return <LoadingPage />;
  }
  if (!predictions) {
    return <div>Error fetching predictions</div>;
  }

  return (
    <div>
      <Header predictions={predictions} />
      <Body predictions={predictions} />
      <Footer />
    </div>
  );
};

export default HomePage;
