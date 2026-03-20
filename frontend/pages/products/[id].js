// pages/products/[id].js – Product detail page
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { fetchProduct, fetchSimilarProducts, postInteraction } from "../../services/api";
import ProductCard from "../../components/ProductCard";
import { CardSkeleton } from "../../components/Skeleton";
import ErrorState from "../../components/ErrorState";

export default function ProductDetailPage({ userId = 1 }) {
  const router = useRouter();
  const { id }  = router.query;

  const [product, setProduct]   = useState(null);
  const [similar, setSimilar]   = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [rating, setRating]     = useState(null);
  const [hover, setHover]       = useState(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);

    Promise.all([
      fetchProduct(id),
      fetchSimilarProducts(id, 6),
    ])
      .then(([p, s]) => {
        setProduct(p);
        setSimilar(s.items || []);
        // track view
        postInteraction({ user_id: userId, product_id: parseInt(id), interaction_type: "view" }).catch(() => {});
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id, userId]);

  const handleRate = async (stars) => {
    if (submitted) return;
    setRating(stars);
    try {
      await postInteraction({ user_id: userId, product_id: parseInt(id), rating: stars, interaction_type: "purchase" });
      setSubmitted(true);
    } catch (_) {}
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-16">
          <div className="h-96 bg-slate-100 rounded-2xl animate-pulse" />
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className={`h-${i === 0 ? 8 : 4} bg-slate-100 rounded animate-pulse w-${i === 0 ? "3/4" : "full"}`} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return <ErrorState message={error || "Product not found"} onRetry={() => router.reload()} />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-slate-400 mb-8">
        <Link href="/" className="hover:text-indigo-600 transition-colors">Home</Link>
        <span>/</span>
        <Link href="/products" className="hover:text-indigo-600 transition-colors">Products</Link>
        <span>/</span>
        <span className="text-slate-700 font-medium truncate max-w-xs">{product.name}</span>
      </nav>

      {/* Main */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-16">
        {/* Image */}
        <div className="rounded-2xl overflow-hidden bg-slate-50 border border-slate-100 aspect-square">
          <img
            src={product.image_url || `https://picsum.photos/seed/${product.id + 10}/600/600`}
            alt={product.name}
            className="w-full h-full object-cover"
          />
        </div>

        {/* Info */}
        <div className="flex flex-col gap-5">
          <div>
            <span className="inline-block text-xs font-semibold bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full mb-3">
              {product.category}
            </span>
            <h1 className="text-3xl font-extrabold text-slate-900 leading-tight">{product.name}</h1>
          </div>

          {/* Rating */}
          <div className="flex items-center gap-2">
            <div className="flex">
              {[1,2,3,4,5].map((s) => (
                <svg key={s} className={`w-5 h-5 ${s <= Math.round(product.rating_avg || 0) ? "text-amber-400" : "text-slate-200"}`}
                  fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
            <span className="font-semibold text-slate-700">{Number(product.rating_avg).toFixed(1)}</span>
            <span className="text-slate-400 text-sm">· {product.stock} in stock</span>
          </div>

          <p className="text-slate-600 leading-relaxed">{product.description}</p>

          <div className="text-4xl font-extrabold text-slate-900">
            ${Number(product.price).toFixed(2)}
          </div>

          {/* Rate this product */}
          <div className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
            <p className="text-sm font-semibold text-slate-700 mb-3">
              {submitted ? "✅ Thanks for your rating!" : "Rate this product"}
            </p>
            <div className="flex gap-2">
              {[1,2,3,4,5].map((s) => (
                <button
                  key={s}
                  onMouseEnter={() => setHover(s)}
                  onMouseLeave={() => setHover(null)}
                  onClick={() => handleRate(s)}
                  disabled={submitted}
                  className="transition-transform hover:scale-125 disabled:cursor-default"
                >
                  <svg className={`w-8 h-8 transition-colors ${s <= (hover ?? rating ?? 0) ? "text-amber-400" : "text-slate-200"}`}
                    fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Similar products */}
      {similar.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Similar Products</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-5">
            {similar.map((p) => (
              <ProductCard key={p.id} product={p} userId={userId} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
