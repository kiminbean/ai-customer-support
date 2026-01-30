import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex h-[100vh] w-full flex-col items-center justify-center bg-gray-50 px-4 text-center">
      <div className="flex max-w-md flex-col items-center justify-center space-y-6">
        <div className="relative">
          <div className="absolute -inset-4 rounded-full bg-blue-100 opacity-50 blur-lg"></div>
          <h1 className="relative text-9xl font-black text-[#2563EB] opacity-10">
            404
          </h1>
          <div className="absolute inset-0 flex items-center justify-center">
            <svg
              className="h-20 w-20 text-[#2563EB]"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="1.5"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
              />
            </svg>
          </div>
        </div>
        
        <div className="space-y-2">
          <h2 className="text-2xl font-bold tracking-tight text-gray-900">
            페이지를 찾을 수 없습니다
          </h2>
          <p className="text-gray-500">
            요청하신 페이지가 존재하지 않거나 이동되었습니다.
          </p>
        </div>

        <Link
          href="/"
          className="rounded-lg bg-[#2563EB] px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-[#1d4ed8] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563EB] transition-colors duration-200"
        >
          홈으로 돌아가기
        </Link>
      </div>
    </div>
  );
}
