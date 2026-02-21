"use client";

interface LoadingSkeletonProps {
  variant?: "text" | "card" | "list" | "table" | "chart";
  count?: number;
  className?: string;
}

export function LoadingSkeleton({
  variant = "text",
  count = 1,
  className = "",
}: LoadingSkeletonProps) {
  const baseClasses = "animate-pulse bg-gray-200 rounded";

  const variants = {
    text: `${baseClasses} h-4 w-full`,
    card: `${baseClasses} h-32 w-full rounded-xl`,
    list: `${baseClasses} h-16 w-full rounded-lg`,
    table: `${baseClasses} h-12 w-full`,
    chart: `${baseClasses} h-48 w-full rounded-xl`,
  };

  const items = Array.from({ length: count }, (_, i) => i);

  if (variant === "list") {
    return (
      <div className={`space-y-3 ${className}`}>
        {items.map((i) => (
          <div
            key={i}
            className={`${variants.list} flex items-center gap-3 p-3`}
          >
            <div className="w-10 h-10 bg-gray-300 rounded-full shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="h-3 bg-gray-300 rounded w-1/3" />
              <div className="h-3 bg-gray-300 rounded w-2/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (variant === "table") {
    return (
      <div className={`${className}`}>
        <div className={`${variants.table} mb-2`} />
        {items.map((i) => (
          <div key={i} className="flex gap-4 mb-2 p-3 border-b border-gray-100">
            <div className="h-4 bg-gray-200 rounded w-1/4" />
            <div className="h-4 bg-gray-200 rounded w-1/4" />
            <div className="h-4 bg-gray-200 rounded w-1/4" />
            <div className="h-4 bg-gray-200 rounded w-1/4" />
          </div>
        ))}
      </div>
    );
  }

  if (variant === "chart") {
    return (
      <div className={`${variants.chart} ${className}`}>
        <div className="flex items-end justify-around h-full p-4 pt-8">
          {items.slice(0, 7).map((i) => (
            <div
              key={i}
              className="w-8 bg-gray-300 rounded-t"
              style={{ height: `${20 + Math.random() * 60}%` }}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {items.map((i) => (
        <div key={i} className={variants[variant]} />
      ))}
    </div>
  );
}

export function PageLoadingSpinner() {
  return (
    <div className="min-h-[400px] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-4 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-500">로딩 중...</p>
      </div>
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 animate-pulse">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-gray-200 rounded-full" />
        <div className="flex-1">
          <div className="h-3 bg-gray-200 rounded w-1/2 mb-2" />
          <div className="h-2 bg-gray-200 rounded w-1/3" />
        </div>
      </div>
      <div className="space-y-2">
        <div className="h-3 bg-gray-200 rounded w-full" />
        <div className="h-3 bg-gray-200 rounded w-4/5" />
        <div className="h-3 bg-gray-200 rounded w-3/5" />
      </div>
    </div>
  );
}

export default LoadingSkeleton;
