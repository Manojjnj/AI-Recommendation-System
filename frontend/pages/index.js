// pages/index.js – Home Page
import { useState, useEffect, useCallback } from "react";
import { fetchRecommendations, fetchTrendingProducts } from "../services/api";
import ProductCard from "../components/ProductCard";
import SectionHeader from "../components/SectionHeader";
import { GridSkeleton } from "../components/Skeleton";
import ErrorState from "../components/ErrorState";
import Link from "next/link";

const STRATEGIES = [
  { value: "hybrid",        label: "🧠 Hybrid",        desc: "Best of both worlds" },
  { value: "collaborative", label: "👥 Collaborative",  desc: "Similar users" },
  { value: "content",       label: "📄 Content",        desc: "Product similarity" },
];

export default function HomePage({ userId = 1 }) {
  const [strategy, setStrategy]         = useState("hybrid");
  const [recommendations, setRecs]      = useState([]);
  const [trending, setTrending]         = useState([]);
  const [loadingRecs, setLoadingRecs]   = useState(true);
  const [loadingTrend, setLoadingTrend] = useState(true);
  const [errorRecs, setErrorRecs]       = useState(null);
  const [errorTrend, setErrorTrend]     = useState(null);

  const loadRecommendations = useCallback(async () => {
    setLoadingRecs(true);
    setErrorRecs(null);
    try {
      const data = await fetchRecommendations(userId, { n: 8, strategy });
      setRecs(data.recommendations || []);
    } catch (e) {
      setErrorRecs(e.message);
    } finally {
      setLoadingRecs(false);
    }
  }, [userId, strategy]);

  const loadTrending = useCallback(async () => {
    setLoadingTrend(true);
    setErrorTrend(null);
    try {
      const data = await fetchTrendingProducts(8);
      setTrending(data.items || []);
    } catch (e) {
      setErrorTrend(e.message);
    } finally {
      setLoadingTrend(false);
    }
  }, []);

  useEffect(() => { loadRecommendations(); }, [loadRecommendations]);
  useEffect(() => { loadTrending(); }, [loadTrending]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Hero */}
      <div className="relative rounded-3xl bg-gradient-to-br from-indigo-600 via-purple-600 to-blue-700 text-white px-8 py-14 mb-14 overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-96 h-96 bg-white rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-white rounded-full translate-y-1/2 -translate-x-1/2" />
        </div>
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-1.5 mb-5 text-sm font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-300 animate-pulse" />
            ML Recommendations Active
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4 leading-tight">
            Products <br />
            <span className="text-indigo-200">Curated For You</span>
          </h1>
          <p className="text-indigo-100 text-lg leading-relaxed max-w-lg">
            Our hybrid AI engine combines collaborative filtering and content-based ML
            to surface products you'll actually want.
          </p>
          <div className="flex flex-wrap gap-3 mt-8">
            <Link href="/products"
              className="px-6 py-3 rounded-xl bg-white text-indigo-700 font-semibold text-sm hover:bg-indigo-50 transition-colors shadow-lg">
              Browse All Products
            </Link>
            <Link href="/dashboard"
              className="px-6 py-3 rounded-xl bg-white/10 border border-white/30 text-white font-semibold text-sm hover:bg-white/20 transition-colors">
              My Dashboard →
            </Link>
          </div>
        </div>
        <div className="absolute bottom-6 right-8 text-right text-white/60 text-sm">
          Viewing as <span className="font-semibold text-white">User #{userId}</span>
        </div>
      </div>

      {/* Recommendations */}
      <section className="mb-16">
        <SectionHeader
          badge="Personalised"
          title="Recommended For You"
          subtitle={`Top picks for User #${userId} using ${strategy} filtering`}
          action={
            <div className="flex gap-2 flex-wrap justify-end">
              {STRATEGIES.map((s) => (
                <button
                  key={s.value}
                  onClick={() => setStrategy(s.value)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    strategy === s.value
                      ? "bg-indigo-600 text-white shadow-md"
                      : "bg-white text-slate-600 border border-slate-200 hover:border-indigo-300"
                  }`}
                  title={s.desc}
                >
                  {s.label}
                </button>
              ))}
            </div>
          }
        />

        {loadingRecs ? (
          <GridSkeleton count={8} />
        ) : errorRecs ? (
          <ErrorState message={errorRecs} onRetry={loadRecommendations} />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {recommendations.map((p) => (
              <ProductCard key={p.id} product={p} userId={userId} showScore />
            ))}
          </div>
        )}
      </section>

      {/* Trending */}
      <section>
        <SectionHeader
          badge="🔥 Hot right now"
          title="Trending Products"
          subtitle="Most interacted with in the past 30 days"
        />
        {loadingTrend ? (
          <GridSkeleton count={8} />
        ) : errorTrend ? (
          <ErrorState message={errorTrend} onRetry={loadTrending} />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {trending.map((p) => (
              <ProductCard key={p.id} product={p} userId={userId} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
