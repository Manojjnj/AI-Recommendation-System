// pages/dashboard.js – User Dashboard
import { useState, useEffect, useCallback } from "react";
import { fetchRecommendations, fetchUserInteractions, fetchUser } from "../services/api";
import ProductCard from "../components/ProductCard";
import SectionHeader from "../components/SectionHeader";
import { GridSkeleton, StatSkeleton } from "../components/Skeleton";
import ErrorState from "../components/ErrorState";
import Link from "next/link";

export default function DashboardPage({ userId = 1 }) {
  const [user, setUser]             = useState(null);
  const [recs, setRecs]             = useState([]);
  const [history, setHistory]       = useState([]);
  const [strategy, setStrategy]     = useState("hybrid");
  const [loadingUser, setLoadingUser] = useState(true);
  const [loadingRecs, setLoadingRecs] = useState(true);
  const [loadingHist, setLoadingHist] = useState(true);

  useEffect(() => {
    setLoadingUser(true);
    fetchUser(userId)
      .then(setUser)
      .catch(() => setUser({ id: userId, name: `User #${userId}`, email: "—" }))
      .finally(() => setLoadingUser(false));
  }, [userId]);

  const loadRecs = useCallback(async () => {
    setLoadingRecs(true);
    try {
      const data = await fetchRecommendations(userId, { n: 8, strategy });
      setRecs(data.recommendations || []);
    } catch (_) {
      setRecs([]);
    } finally {
      setLoadingRecs(false);
    }
  }, [userId, strategy]);

  useEffect(() => { loadRecs(); }, [loadRecs]);

  useEffect(() => {
    setLoadingHist(true);
    fetchUserInteractions(userId, 10)
      .then((d) => setHistory(d.interactions || []))
      .catch(() => setHistory([]))
      .finally(() => setLoadingHist(false));
  }, [userId]);

  const STRATEGIES = ["hybrid", "collaborative", "content"];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* User card */}
      <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-3xl p-8 text-white mb-10 flex items-center gap-6">
        <div className="w-20 h-20 rounded-2xl bg-white/20 flex items-center justify-center text-4xl font-bold shrink-0">
          {loadingUser ? "…" : (user?.name?.[0] || "U")}
        </div>
        <div>
          <p className="text-indigo-200 text-sm font-medium mb-1">Welcome back</p>
          <h1 className="text-3xl font-extrabold">{loadingUser ? "Loading…" : user?.name}</h1>
          <p className="text-indigo-200 text-sm mt-1">{user?.email}</p>
        </div>
        <div className="ml-auto text-right hidden sm:block">
          <p className="text-indigo-200 text-xs">User ID</p>
          <p className="text-4xl font-black">#{userId}</p>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {[
          { label: "Interactions",  value: history.length, icon: "🖱️" },
          { label: "Strategy",      value: strategy,        icon: "🧠" },
          { label: "Recs Ready",    value: recs.length,     icon: "✨" },
          { label: "Top Category",  value: history[0]?.product_name?.split(" ")[0] || "—", icon: "🏆" },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
            <div className="text-2xl mb-2">{s.icon}</div>
            <p className="text-slate-400 text-xs font-medium uppercase tracking-wide">{s.label}</p>
            <p className="text-xl font-bold text-slate-800 mt-0.5 truncate">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Recommendations */}
      <section className="mb-14">
        <SectionHeader
          badge="Personalised"
          title="Your Recommendations"
          action={
            <div className="flex gap-2">
              {STRATEGIES.map((s) => (
                <button key={s} onClick={() => setStrategy(s)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
                    strategy === s
                      ? "bg-indigo-600 text-white"
                      : "bg-white border border-slate-200 text-slate-600 hover:border-indigo-300"
                  }`}
                >{s}</button>
              ))}
            </div>
          }
        />
        {loadingRecs
          ? <GridSkeleton count={8} />
          : <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {recs.map((p) => <ProductCard key={p.id} product={p} userId={userId} showScore />)}
            </div>
        }
      </section>

      {/* Interaction history */}
      <section>
        <SectionHeader title="Recent Activity" subtitle="Your last 10 interactions" />
        <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden shadow-sm">
          {loadingHist ? (
            <div className="p-6 space-y-3">{[...Array(5)].map((_, i) => (
              <div key={i} className="h-10 bg-slate-100 rounded-xl animate-pulse" />
            ))}</div>
          ) : history.length === 0 ? (
            <div className="p-12 text-center text-slate-400">
              <p className="text-4xl mb-3">🛍️</p>
              <p>No interactions yet. Start browsing!</p>
              <Link href="/products" className="mt-4 inline-block px-5 py-2 bg-indigo-600 text-white rounded-xl text-sm font-medium">
                Browse Products
              </Link>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  {["Product", "Type", "Rating", "Date"].map((h) => (
                    <th key={h} className="text-left px-5 py-3 text-slate-500 font-semibold text-xs uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {history.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3 font-medium text-slate-800 truncate max-w-xs">
                      <Link href={`/products/${row.product_id}`} className="hover:text-indigo-600">
                        {row.product_name}
                      </Link>
                    </td>
                    <td className="px-5 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        row.interaction_type === "purchase"
                          ? "bg-emerald-100 text-emerald-700"
                          : row.interaction_type === "click"
                          ? "bg-blue-100 text-blue-700"
                          : "bg-slate-100 text-slate-600"
                      }`}>{row.interaction_type}</span>
                    </td>
                    <td className="px-5 py-3 text-slate-600">
                      {row.rating ? `${row.rating} ★` : <span className="text-slate-300">—</span>}
                    </td>
                    <td className="px-5 py-3 text-slate-400 text-xs">
                      {new Date(row.timestamp).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  );
}
