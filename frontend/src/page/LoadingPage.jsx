import React from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";

const LoadingPage = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <div className="flex-grow flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl font-semibold text-blue-600 mb-4">
            Loading...
          </div>
          <div className="animate-spin border-t-4 border-blue-600 w-16 h-16 rounded-full mx-auto"></div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default LoadingPage;
