"use client";

import { useState } from "react";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";

export default function WidgetPage() {
  const [chatOpen, setChatOpen] = useState(true);
  const [copied, setCopied] = useState(false);

  const embedCode = `<!-- SupportAI 채팅 위젯 -->
<script>
  (function(w,d,s,o,f,js,fjs){
    w['SupportAI']=o;w[o]=w[o]||function(){
    (w[o].q=w[o].q||[]).push(arguments)};
    js=d.createElement(s);fjs=d.getElementsByTagName(s)[0];
    js.id=o;js.src=f;js.async=1;
    fjs.parentNode.insertBefore(js,fjs);
  }(window,document,'script','supportai',
    'https://cdn.supportai.kr/widget.js'));
  supportai('init', {
    projectId: 'YOUR_PROJECT_ID',
    primaryColor: '#2563EB',
    position: 'bottom-right',
    language: 'ko',
    greeting: '안녕하세요! 무엇을 도와드릴까요?'
  });
</script>`;

  const handleCopy = () => {
    navigator.clipboard.writeText(embedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 pt-16">
      <Navbar variant="app" activePage="widget" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900">임베드 위젯 미리보기</h1>
          <p className="text-gray-500 mt-2">아래 코드를 복사하여 웹사이트에 붙여넣으면 AI 채팅 위젯이 바로 작동합니다</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Preview */}
          <div>
            <h2 className="text-sm font-semibold text-gray-700 mb-3">실제 사이트 미리보기</h2>
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              {/* Fake browser */}
              <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 border-b border-gray-100">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-yellow-400" />
                  <div className="w-3 h-3 rounded-full bg-green-400" />
                </div>
                <div className="flex-1 bg-white rounded-md px-3 py-1 text-xs text-gray-400 text-center border border-gray-200">
                  https://your-store.com
                </div>
              </div>
              {/* Fake website content */}
              <div className="relative h-[540px] p-6 bg-gradient-to-br from-gray-50 to-white overflow-hidden">
                {/* Fake e-commerce content */}
                <div className="space-y-4">
                  <div className="h-6 w-32 bg-gray-200 rounded animate-pulse" />
                  <div className="grid grid-cols-3 gap-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="bg-white rounded-lg border border-gray-100 p-3">
                        <div className="w-full h-20 bg-gray-100 rounded-md mb-2" />
                        <div className="h-3 w-full bg-gray-100 rounded mb-1" />
                        <div className="h-3 w-2/3 bg-gray-100 rounded mb-2" />
                        <div className="h-4 w-1/2 bg-blue-100 rounded" />
                      </div>
                    ))}
                  </div>
                  <div className="h-4 w-full bg-gray-100 rounded" />
                  <div className="h-4 w-3/4 bg-gray-100 rounded" />
                  <div className="h-4 w-5/6 bg-gray-100 rounded" />
                  <div className="grid grid-cols-2 gap-3 mt-4">
                    {[1, 2].map((i) => (
                      <div key={i} className="bg-white rounded-lg border border-gray-100 p-3">
                        <div className="w-full h-24 bg-gray-100 rounded-md mb-2" />
                        <div className="h-3 w-full bg-gray-100 rounded mb-1" />
                        <div className="h-3 w-1/2 bg-gray-100 rounded" />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Chat widget overlay */}
                {chatOpen ? (
                  <div className="absolute bottom-4 right-4 w-72 bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden animate-fade-in-up">
                    {/* Widget header */}
                    <div className="bg-[#2563EB] px-4 py-3 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                          </svg>
                        </div>
                        <div>
                          <div className="text-white text-xs font-semibold">고객지원 봇</div>
                          <div className="flex items-center gap-1">
                            <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
                            <span className="text-blue-100 text-[10px]">온라인</span>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => setChatOpen(false)}
                        className="text-white/80 hover:text-white"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                    </div>
                    {/* Widget messages */}
                    <div className="p-3 space-y-2 h-40 overflow-y-auto bg-gray-50/50">
                      <div className="flex items-start gap-2">
                        <div className="w-6 h-6 rounded-full bg-[#2563EB] flex items-center justify-center shrink-0">
                          <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <div className="bg-white text-[11px] text-gray-700 px-3 py-2 rounded-xl rounded-tl-sm shadow-sm border border-gray-100">
                          안녕하세요! 👋 무엇을 도와드릴까요?
                        </div>
                      </div>
                      <div className="flex justify-end">
                        <div className="bg-[#2563EB] text-white text-[11px] px-3 py-2 rounded-xl rounded-tr-sm">
                          배송이 언제 도착하나요?
                        </div>
                      </div>
                      <div className="flex items-start gap-2">
                        <div className="w-6 h-6 rounded-full bg-[#2563EB] flex items-center justify-center shrink-0">
                          <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <div className="bg-white text-[11px] text-gray-700 px-3 py-2 rounded-xl rounded-tl-sm shadow-sm border border-gray-100">
                          주문번호를 알려주시면 바로 확인해드리겠습니다! 📦
                        </div>
                      </div>
                    </div>
                    {/* Widget input */}
                    <div className="p-2 border-t border-gray-100 bg-white">
                      <div className="flex gap-1.5">
                        <input
                          type="text"
                          placeholder="메시지를 입력하세요..."
                          className="flex-1 px-3 py-1.5 bg-gray-100 rounded-lg text-[11px] focus:outline-none"
                          readOnly
                        />
                        <button className="px-2.5 py-1.5 bg-[#2563EB] text-white rounded-lg">
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setChatOpen(true)}
                    className="absolute bottom-4 right-4 w-14 h-14 bg-[#2563EB] rounded-full shadow-lg flex items-center justify-center text-white hover:bg-[#1d4ed8] transition-all pulse-glow"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">
              위젯 아이콘을 클릭하여 열고 닫을 수 있습니다
            </p>
          </div>

          {/* Embed code */}
          <div>
            <h2 className="text-sm font-semibold text-gray-700 mb-3">임베드 코드</h2>
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-100">
                <span className="text-xs font-medium text-gray-500">HTML</span>
                <button
                  onClick={handleCopy}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                    copied
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  {copied ? "✓ 복사됨!" : "📋 코드 복사"}
                </button>
              </div>
              <pre className="p-4 text-xs text-gray-700 overflow-x-auto bg-gray-900 text-gray-300 font-mono leading-relaxed">
                <code>{embedCode}</code>
              </pre>
            </div>

            {/* Instructions */}
            <div className="mt-6 bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <h3 className="text-sm font-semibold text-gray-900 mb-4">설치 방법</h3>
              <div className="space-y-4">
                {[
                  {
                    step: 1,
                    title: "코드 복사",
                    desc: "위의 코드를 복사합니다. 'YOUR_PROJECT_ID'를 실제 프로젝트 ID로 교체하세요.",
                  },
                  {
                    step: 2,
                    title: "HTML에 삽입",
                    desc: "웹사이트의 </body> 태그 바로 앞에 코드를 붙여넣습니다.",
                  },
                  {
                    step: 3,
                    title: "설정 커스터마이즈",
                    desc: "primaryColor, position, language 등의 옵션을 변경하여 원하는 대로 설정합니다.",
                  },
                  {
                    step: 4,
                    title: "배포",
                    desc: "변경 사항을 배포하면 즉시 위젯이 활성화됩니다!",
                  },
                ].map((item) => (
                  <div key={item.step} className="flex gap-3">
                    <div className="w-7 h-7 bg-[#2563EB] rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0">
                      {item.step}
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{item.title}</h4>
                      <p className="text-xs text-gray-500 mt-0.5">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Supported platforms */}
            <div className="mt-6 bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">지원 플랫폼</h3>
              <div className="grid grid-cols-3 gap-3">
                {["WordPress", "Shopify", "React", "Vue.js", "Wix", "기타 HTML"].map((platform) => (
                  <div
                    key={platform}
                    className="px-3 py-2 bg-gray-50 rounded-lg text-xs text-center text-gray-600 font-medium border border-gray-100"
                  >
                    {platform}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
