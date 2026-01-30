export default function Loading() {
  return (
    <div className="flex h-[100vh] w-full flex-col items-center justify-center bg-gray-50">
      <div className="flex flex-col items-center gap-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-[#2563EB]"></div>
        <p className="text-sm font-medium text-gray-500 animate-pulse">
          로딩 중...
        </p>
      </div>
    </div>
  );
}
