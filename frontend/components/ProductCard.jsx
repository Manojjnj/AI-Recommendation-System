// components/ProductCard.jsx
import { useState } from "react";
import Link from "next/link";
import { postInteraction } from "../services/api";

const CATEGORY_COLORS = {
  Electronics: "bg-blue-100 text-blue-700",
  Books: "bg-amber-100 text-amber-700",
  "Clothing": "bg-pink-100 text-pink-700",
  "Home & Kitchen": "bg-green-100 text-green-700",
  Sports: "bg-orange-100 text-orange-700",
  Beauty: "bg-purple-100 text-purple-700",
  Toys: "bg-red-100 text-red-700",
};

export default function ProductCard({ product, userId = 1, showScore = false }) {
  const [rating, setRating] = useState(null);
  const [hoverRating, setHoverRating] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleRate = async (stars) => {
    if (submitting || submitted) return;
    setRating(stars);
    setSubmitting(true);
    try {
      await postInteraction({ user_id: userId, product_id: product.id, rating: stars, interaction_type: "purchase" });
      setSubmitted(true);
    } catch (_) {
      // silent – offline demo
    } finally {
      setSubmitting(false);
    }
  };

  const handleClick = () => {
    postInteraction({ user_id: userId, product_id: product.id, interaction_type: "click" }).catch(() => {});
  };

  const categoryClass = CATEGORY_COLORS[product.category] || "bg-slate-100 text-slate-600";
  const displayScore = product.score != null ? Math.round(product.score * 100) : null;

  return (
    <div className="group relative bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden flex flex-col">
      {/* Score badge */}
      {showScore && displayScore != null && (
        <div className="absolute top-3 right-3 z-10 bg-indigo-600 text-white text-xs font-bold px-2 py-1 rounded-full shadow">
          {displayScore}% match
        </div>
      )}

      {/* Image */}
      <Link href={`/products/${product.id}`} onClick={handleClick}>
        <div className="relative h-48 overflow-hidden bg-slate-50">
          <img
            src={product.image_url || `https://picsum.photos/seed/${product.id + 10}/400/300`}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </Link>

      {/* Body */}
      <div className="flex flex-col flex-1 p-4 gap-2">
        <span className={`self-start text-xs font-semibold px-2 py-0.5 rounded-full ${categoryClass}`}>
          {product.category}
        </span>

        <Link href={`/products/${product.id}`} onClick={handleClick}>
          <h3 className="font-semibold text-slate-800 text-sm leading-snug line-clamp-2 hover:text-indigo-600 transition-colors cursor-pointer">
            {product.name}
          </h3>
        </Link>

        {product.reason && (
          <p className="text-xs text-slate-400 italic line-clamp-1">{product.reason}</p>
        )}

        {/* Avg rating */}
        <div className="flex items-center gap-1 mt-auto">
          {[1, 2, 3, 4, 5].map((s) => (
            <svg
              key={s}
              className={`w-3.5 h-3.5 ${s <= Math.round(product.rating_avg || 0) ? "text-amber-400" : "text-slate-200"}`}
              fill="currentColor" viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          ))}
          <span className="text-xs text-slate-400 ml-1">{Number(product.rating_avg || 0).toFixed(1)}</span>
        </div>

        {/* Price + rate */}
        <div className="flex items-center justify-between mt-1">
          <span className="text-lg font-bold text-slate-900">${Number(product.price).toFixed(2)}</span>

          {/* Star rating input */}
          <div className="flex gap-0.5">
            {[1, 2, 3, 4, 5].map((s) => (
              <button
                key={s}
                onMouseEnter={() => setHoverRating(s)}
                onMouseLeave={() => setHoverRating(null)}
                onClick={() => handleRate(s)}
                disabled={submitted}
                title={`Rate ${s} stars`}
                className="transition-transform hover:scale-125 disabled:cursor-default"
              >
                <svg
                  className={`w-4 h-4 transition-colors ${
                    s <= (hoverRating ?? rating ?? 0)
                      ? "text-amber-400"
                      : "text-slate-200"
                  }`}
                  fill="currentColor" viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </button>
            ))}
          </div>
        </div>
        {submitted && <p className="text-xs text-emerald-500 font-medium">✓ Rating saved!</p>}
      </div>
    </div>
  );
}
