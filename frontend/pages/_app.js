// pages/_app.js
import { useState, useEffect } from "react";
import "../styles/globals.css";
import Navbar from "../components/Navbar";

export default function App({ Component, pageProps }) {
  const [userId, setUserId] = useState(1);

  useEffect(() => {
    const saved = localStorage.getItem("userId");
    if (saved) setUserId(parseInt(saved, 10));
  }, []);

  const handleUserChange = (id) => {
    setUserId(id);
    localStorage.setItem("userId", String(id));
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <Navbar userId={userId} onUserChange={handleUserChange} />
      <main>
        <Component {...pageProps} userId={userId} />
      </main>
      <footer className="mt-20 border-t border-slate-100 py-8 text-center text-slate-400 text-sm">
        <p>RecoAI — Intelligent E-commerce Recommendations © 2025</p>
        <p className="mt-1 text-xs text-slate-300">
          Powered by Collaborative Filtering + Content-Based ML
        </p>
      </footer>
    </div>
  );
}
