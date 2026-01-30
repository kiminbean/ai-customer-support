'use client';

import { useEffect } from 'react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
    if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
      import('@sentry/nextjs').then((Sentry) => {
        Sentry.captureException(error);
      }).catch(() => {});
    }
  }, [error]);

  return (
    <div className="flex h-[100vh] w-full flex-col items-center justify-center bg-gray-50 px-4 text-center">
      <div className="flex max-w-md flex-col items-center justify-center space-y-6 rounded-2xl bg-white p-8 shadow-xl ring-1 ring-gray-900/5">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
          <svg
            className="h-8 w-8 text-red-600"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
            />
          </svg>
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold tracking-tight text-gray-900">
            오류가 발생했습니다
          </h2>
          <p className="text-gray-500">
            예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.
          </p>
        </div>
        <button
          onClick={() => reset()}
          className="rounded-lg bg-[#2563EB] px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-[#1d4ed8] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB] transition-colors duration-200"
        >
          다시 시도
        </button>
      </div>
    </div>
  );
}
