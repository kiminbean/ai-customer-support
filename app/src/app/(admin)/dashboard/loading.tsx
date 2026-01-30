export default function DashboardLoading() {
  return (
    <div className="flex h-screen w-full bg-gray-50 overflow-hidden">
      <div className="hidden w-64 flex-col border-r border-gray-200 bg-white md:flex">
        <div className="flex h-16 items-center px-6">
          <div className="h-6 w-32 animate-pulse rounded bg-gray-200"></div>
        </div>
        <div className="flex flex-1 flex-col gap-4 px-4 py-6">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-10 animate-pulse rounded-lg bg-gray-100"
            ></div>
          ))}
        </div>
      </div>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 items-center border-b border-gray-200 bg-white px-6">
          <div className="h-6 w-48 animate-pulse rounded bg-gray-200"></div>
        </header>

        <main className="flex-1 overflow-auto p-6">
          <div className="grid gap-6">
            <div className="flex items-center justify-between">
              <div className="h-8 w-64 animate-pulse rounded bg-gray-200"></div>
              <div className="h-8 w-24 animate-pulse rounded bg-gray-200"></div>
            </div>
            
            <div className="grid gap-6 md:grid-cols-3">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="h-32 animate-pulse rounded-xl bg-white shadow-sm ring-1 ring-gray-900/5"
                ></div>
              ))}
            </div>

            <div className="h-96 animate-pulse rounded-xl bg-white shadow-sm ring-1 ring-gray-900/5">
              <div className="flex h-full items-center justify-center">
                <p className="text-sm font-medium text-gray-400">
                  대시보드 로딩 중...
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
