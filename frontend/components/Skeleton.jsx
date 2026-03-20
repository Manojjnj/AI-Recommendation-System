// components/Skeleton.jsx – reusable loading placeholder

export function CardSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden animate-pulse">
      <div className="h-48 bg-slate-100" />
      <div className="p-4 space-y-3">
        <div className="h-4 bg-slate-100 rounded w-1/3" />
        <div className="h-4 bg-slate-100 rounded w-4/5" />
        <div className="h-3 bg-slate-100 rounded w-2/3" />
        <div className="flex justify-between mt-4">
          <div className="h-6 bg-slate-100 rounded w-1/4" />
          <div className="h-6 bg-slate-100 rounded w-1/4" />
        </div>
      </div>
    </div>
  );
}

export function GridSkeleton({ count = 8 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

export function StatSkeleton() {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 animate-pulse">
      <div className="h-4 bg-slate-100 rounded w-1/2 mb-3" />
      <div className="h-8 bg-slate-100 rounded w-1/3" />
    </div>
  );
}
