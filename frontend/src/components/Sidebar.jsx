import React from "react";
import { Link } from "react-router-dom";

const Sidebar = () => {
  return (
    <aside className="w-1/6 bg-blue-700 text-white p-4 rounded-lg shadow-md mr-6">
      <h2 className="text-lg font-semibold mb-4">Past</h2>
      <ul>
        <li className="mb-2">
          <Link to="/" className="hover:underline">
            Home
          </Link>
        </li>
        <li className="mb-2">
          <Link to="/recap" className="hover:underline">
            Yesterday's Recap
          </Link>
        </li>
      </ul>
    </aside>
  );
};

export default Sidebar;
