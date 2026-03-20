// pages/analytics.js – Analytics Dashboard
import { useState, useEffect } from "react";
import { fetchDashboard } from "../services/api";
import SectionHeader from "../components/SectionHeader";
import ErrorState from "../components/ErrorState";
import { StatSkeleton } from "../components/Skeleton";
import Link from "next/link";

function StatCard({ icon, label, value, sub, color = "indigo" }) {
  const colorMap = {
    indigo: "from-indigo-500 to-indigo-600",
    purple: "from-purple-500 to-purple-600",
    emerald: "from-emerald-500 to-emerald-600",
    amber: "from-amber-500 to-amber-600",
  };
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm flex items-start gap-4">
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorMap[color]} flex items-center justify-center text-2xl shrink-0`}>
        {icon}
      </div>
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</p>
        <p className="text-3xl font-extrabold text-slate-900 mt-1">{value}</p>
        {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

function MiniBar({ label, value, max }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-slate-600 w-36 shrink-0 truncate">{label}</span>
      <div className="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs font-semibold text-slate-500 w-8 text-right">{value}</span>
    </div>
  );
}

export default function AnalyticsPage() {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  const load = () => {
    setLoading(true);
    setError(null);
    fetchDashboard()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="h-8 bg-slate-100 rounded w-48 mb-8 animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => <StatSkeleton key={i} />)}
        </div>
      </div>
    );
  }

  if (error) return <ErrorState message={error} onRetry={load} />;

  const maxCat = Math.max(...(data?.top_categories?.map((c) => c.count) || [1]));
  const ml     = data?.ml_stats || {};

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <SectionHeader
        title="Analytics Dashboard"
        subtitle="System-wide statistics and ML model performance"
        badge="Live"
      />

      {/* KPI cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <StatCard icon="👥" label="Total Users"    value={data.total_users?.toLocaleString()}       color="indigo" />
        <StatCard icon="📦" label="Products"       value={data.total_products?.toLocaleString()}    color="purple" />
        <StatCard icon="🖱️" label="Interactions"   value={data.total_interactions?.toLocaleString()} color="emerald" />
        <StatCard icon="🧠" label="Matrix Size"    value={ml.matrix_shape ? `${ml.matrix_shape[0]}×${ml.matrix_shape[1]}` : "—"} sub="user × product" color="amber" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        {/* Top categories */}
        <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
          <h3 className="font-bold text-slate-800 mb-5">Top Categories by Interactions</h3>
          <div className="flex flex-col gap-3">
            {(data.top_categories || []).map((cat) => (
              <MiniBar key={cat.category} label={cat.category} value={cat.count} max={maxCat} />
            ))}
          </div>
        </div>

        {/* Trending products */}
        <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
          <h3 className="font-bold text-slate-800 mb-5">🔥 Trending Products</h3>
          <div className="flex flex-col gap-3">
            {(data.trending_products || []).slice(0, 5).map((p, i) => (
              <Link key={p.id} href={`/products/${p.id}`}
                className="flex items-center gap-3 hover:bg-slate-50 rounded-xl p-2 transition-colors group">
                <span className="w-7 h-7 rounded-lg bg-slate-100 text-slate-500 text-xs font-bold flex items-center justify-center shrink-0">
                  {i + 1}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-800 truncate group-hover:text-indigo-600">{p.name}</p>
                  <p className="text-xs text-slate-400">{p.category}</p>
                </div>
                <span className="text-xs font-bold text-indigo-600 shrink-0">
                  {Math.round((p.score || 0) * 100)}%
                </span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* ML model stats */}
      <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm mb-10">
        <h3 className="font-bold text-slate-800 mb-4">ML Model Status</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { label: "Status",      value: ml.fitted ? "✅ Ready" : "⏳ Loading" },
            { label: "Users",       value: ml.n_users || "—" },
            { label: "Products",    value: ml.n_products || "—" },
            { label: "Interactions", value: ml.n_interactions || "—" },
          ].map((s) => (
            <div key={s.label}>
              <p className="text-xs text-slate-400 uppercase tracking-wide font-semibold">{s.label}</p>
              <p className="text-lg font-bold text-slate-800 mt-1">{s.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* A/B Experiments */}
      <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
        <h3 className="font-bold text-slate-800 mb-4">A/B Experiments</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                {["Name", "Variant A", "Variant B", "Status"].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-slate-500 font-semibold text-xs uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {(data.ab_experiments || []).map((exp) => (
                <tr key={exp.name} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-800">{exp.name}</td>
                  <td className="px-4 py-3 text-slate-600">{exp.variant_a}</td>
                  <td className="px-4 py-3 text-slate-600">{exp.variant_b}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      exp.is_active ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"
                    }`}>{exp.is_active ? "Active" : "Paused"}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
