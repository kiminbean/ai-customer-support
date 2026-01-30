import Link from "next/link";

function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#2563EB] rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-900">SupportAI</span>
          </Link>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">기능</a>
            <a href="#pricing" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">요금제</a>
            <Link href="/demo" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">데모</Link>
            <Link href="/dashboard" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">대시보드</Link>
            <Link href="/datahub" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">데이터 허브</Link>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="text-sm text-gray-600 hover:text-gray-900 transition-colors hidden sm:block">
              로그인
            </Link>
            <Link
              href="/demo"
              className="px-4 py-2 bg-[#2563EB] text-white text-sm font-medium rounded-lg hover:bg-[#1d4ed8] transition-colors shadow-sm"
            >
              무료 시작하기
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

function HeroSection() {
  return (
    <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-50 rounded-full text-sm text-[#2563EB] font-medium mb-6">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            새로운 GPT-4o 기반 엔진 출시
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight tracking-tight">
            AI 고객지원 플랫폼으로
            <br />
            <span className="text-[#2563EB]">고객 만족도를 극대화</span>하세요
          </h1>
          <p className="mt-6 text-lg sm:text-xl text-gray-500 max-w-2xl mx-auto leading-relaxed">
            24시간 자동 응답, 다국어 지원, 실시간 분석까지.
            <br className="hidden sm:block" />
            AI가 고객지원의 새로운 기준을 만듭니다.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/demo"
              className="px-8 py-3.5 bg-[#2563EB] text-white font-semibold rounded-xl hover:bg-[#1d4ed8] transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 text-base"
            >
              무료 데모 체험하기 →
            </Link>
            <Link
              href="/widget"
              className="px-8 py-3.5 bg-white text-gray-700 font-semibold rounded-xl border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all text-base"
            >
              위젯 미리보기
            </Link>
          </div>
          <div className="mt-8 flex items-center justify-center gap-6 text-sm text-gray-400">
            <span className="flex items-center gap-1.5">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
              신용카드 불필요
            </span>
            <span className="flex items-center gap-1.5">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
              5분 내 설정 완료
            </span>
            <span className="flex items-center gap-1.5">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
              14일 무료 체험
            </span>
          </div>
        </div>

        {/* Hero visual - chat preview */}
        <div className="mt-16 max-w-3xl mx-auto">
          <div className="bg-white rounded-2xl shadow-2xl shadow-gray-200/50 border border-gray-100 overflow-hidden">
            {/* Browser bar */}
            <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 border-b border-gray-100">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-yellow-400" />
                <div className="w-3 h-3 rounded-full bg-green-400" />
              </div>
              <div className="flex-1 text-center text-xs text-gray-400">supportai.kr/chat</div>
            </div>
            {/* Chat preview */}
            <div className="p-6 space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-[#2563EB] flex items-center justify-center shrink-0">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="bg-gray-100 rounded-2xl rounded-tl-md px-4 py-3 max-w-md">
                  <p className="text-sm text-gray-700">안녕하세요! 👋 SupportAI 고객지원 봇입니다. 무엇을 도와드릴까요?</p>
                </div>
              </div>
              <div className="flex items-start gap-3 justify-end">
                <div className="bg-[#2563EB] rounded-2xl rounded-tr-md px-4 py-3 max-w-md">
                  <p className="text-sm text-white">주문한 상품의 배송 상태를 확인하고 싶어요.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-[#2563EB] flex items-center justify-center shrink-0">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="bg-gray-100 rounded-2xl rounded-tl-md px-4 py-3 max-w-md">
                  <p className="text-sm text-gray-700">주문번호를 알려주시면 바로 확인해드리겠습니다. 📦 주문번호는 주문 확인 이메일에서 확인하실 수 있습니다.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
          {[
            { value: "98%", label: "고객 만족도" },
            { value: "0.3초", label: "평균 응답 시간" },
            { value: "50+", label: "지원 언어" },
            { value: "10K+", label: "활성 사용자" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-gray-900">{stat.value}</div>
              <div className="mt-1 text-sm text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function FeaturesSection() {
  const features = [
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: "24/7 자동 응답",
      description: "AI가 고객 문의에 24시간 즉각 대응합니다. 영업 시간에 구애받지 않는 빈틈없는 고객 경험을 제공하세요.",
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
        </svg>
      ),
      title: "다국어 지원",
      description: "50개 이상의 언어를 자동으로 감지하고 번역합니다. 글로벌 고객에게 모국어로 서비스를 제공하세요.",
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      title: "실시간 분석",
      description: "고객 만족도, 응답 시간, 자주 묻는 질문을 실시간으로 분석합니다. 데이터 기반 의사결정을 지원합니다.",
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
      ),
      title: "간편한 설치",
      description: "코드 한 줄이면 기존 웹사이트에 즉시 통합됩니다. 별도의 개발 리소스 없이 5분 만에 설정을 완료하세요.",
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      title: "스마트 학습",
      description: "고객과의 대화에서 지속적으로 학습하여 응답 품질이 향상됩니다. 시간이 지날수록 더 똑똑해지는 AI입니다.",
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      ),
      title: "기업급 보안",
      description: "엔드투엔드 암호화, SOC 2 인증, GDPR 준수. 고객 데이터의 안전을 최우선으로 보장합니다.",
    },
  ];

  return (
    <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 bg-gray-50/50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
            더 똑똑한 고객지원,
            <br />
            <span className="text-[#2563EB]">더 행복한 고객</span>
          </h2>
          <p className="mt-4 text-lg text-gray-500">
            AI 기술로 고객지원의 모든 과정을 자동화하고 최적화합니다
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="bg-white p-6 rounded-2xl border border-gray-100 hover:border-blue-100 hover:shadow-lg hover:shadow-blue-50 transition-all duration-300 group"
            >
              <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-[#2563EB] group-hover:bg-[#2563EB] group-hover:text-white transition-colors duration-300">
                {feature.icon}
              </div>
              <h3 className="mt-4 text-lg font-semibold text-gray-900">{feature.title}</h3>
              <p className="mt-2 text-sm text-gray-500 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function PricingSection() {
  const plans = [
    {
      name: "Free",
      nameKr: "무료",
      price: "₩0",
      period: "/월",
      description: "소규모 팀이 시작하기에 딱 좋은 플랜",
      features: [
        "월 100건 대화",
        "기본 AI 응답",
        "1개 웹사이트 연동",
        "이메일 지원",
        "기본 분석 대시보드",
      ],
      cta: "무료로 시작",
      highlight: false,
    },
    {
      name: "Pro",
      nameKr: "프로",
      price: "₩49,000",
      period: "/월",
      description: "성장하는 비즈니스를 위한 강력한 도구",
      features: [
        "월 5,000건 대화",
        "GPT-4o 기반 고급 AI",
        "무제한 웹사이트 연동",
        "우선 채팅 지원",
        "고급 분석 & 리포트",
        "커스텀 브랜딩",
        "API 액세스",
      ],
      cta: "14일 무료 체험",
      highlight: true,
    },
    {
      name: "Enterprise",
      nameKr: "엔터프라이즈",
      price: "맞춤 견적",
      period: "",
      description: "대규모 조직을 위한 맞춤형 솔루션",
      features: [
        "무제한 대화",
        "전용 AI 모델 학습",
        "전담 매니저",
        "SLA 보장",
        "온프레미스 배포 가능",
        "SSO & 고급 보안",
        "커스텀 통합 개발",
      ],
      cta: "영업팀 문의",
      highlight: false,
    },
  ];

  return (
    <section id="pricing" className="py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
            합리적인 요금제
          </h2>
          <p className="mt-4 text-lg text-gray-500">
            비즈니스 규모에 맞는 플랜을 선택하세요. 언제든 업그레이드할 수 있습니다.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative rounded-2xl p-8 ${
                plan.highlight
                  ? "bg-[#2563EB] text-white ring-4 ring-blue-500/20 scale-105"
                  : "bg-white border border-gray-200"
              }`}
            >
              {plan.highlight && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-yellow-400 text-yellow-900 text-xs font-bold rounded-full">
                  가장 인기 있는 플랜
                </div>
              )}
              <div>
                <span className={`text-sm font-medium ${plan.highlight ? "text-blue-200" : "text-gray-500"}`}>
                  {plan.nameKr}
                </span>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className={`text-sm ${plan.highlight ? "text-blue-200" : "text-gray-400"}`}>
                    {plan.period}
                  </span>
                </div>
                <p className={`mt-2 text-sm ${plan.highlight ? "text-blue-100" : "text-gray-500"}`}>
                  {plan.description}
                </p>
              </div>
              <ul className="mt-8 space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3 text-sm">
                    <svg className={`w-5 h-5 shrink-0 ${plan.highlight ? "text-blue-200" : "text-[#2563EB]"}`} fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <button
                className={`mt-8 w-full py-3 px-4 rounded-xl font-semibold text-sm transition-all ${
                  plan.highlight
                    ? "bg-white text-[#2563EB] hover:bg-blue-50"
                    : "bg-gray-900 text-white hover:bg-gray-800"
                }`}
              >
                {plan.cta}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTASection() {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-[#2563EB] to-blue-700 rounded-3xl p-12 sm:p-16 text-center text-white relative overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute -top-24 -right-24 w-96 h-96 rounded-full border-2 border-white" />
            <div className="absolute -bottom-32 -left-32 w-[500px] h-[500px] rounded-full border-2 border-white" />
          </div>
          <div className="relative">
            <h2 className="text-3xl sm:text-4xl font-bold">
              지금 바로 시작하세요
            </h2>
            <p className="mt-4 text-lg text-blue-100 max-w-xl mx-auto">
              5분 만에 AI 고객지원을 도입하고, 고객 만족도를 높여보세요.
              첫 14일은 무료입니다.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/demo"
                className="px-8 py-3.5 bg-white text-[#2563EB] font-semibold rounded-xl hover:bg-blue-50 transition-colors"
              >
                무료 데모 체험하기
              </Link>
              <Link
                href="/widget"
                className="px-8 py-3.5 bg-white/10 text-white font-semibold rounded-xl border border-white/25 hover:bg-white/20 transition-colors"
              >
                위젯 미리보기
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-[#2563EB] rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <span className="text-lg font-bold text-gray-900">SupportAI</span>
            </div>
            <p className="mt-3 text-sm text-gray-500">
              AI 기반 차세대 고객지원 플랫폼
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">제품</h4>
            <ul className="space-y-2 text-sm text-gray-500">
              <li><a href="#features" className="hover:text-gray-700">기능</a></li>
              <li><a href="#pricing" className="hover:text-gray-700">요금제</a></li>
              <li><Link href="/demo" className="hover:text-gray-700">데모</Link></li>
              <li><Link href="/widget" className="hover:text-gray-700">위젯</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">회사</h4>
            <ul className="space-y-2 text-sm text-gray-500">
              <li><a href="#" className="hover:text-gray-700">소개</a></li>
              <li><a href="#" className="hover:text-gray-700">블로그</a></li>
              <li><a href="#" className="hover:text-gray-700">채용</a></li>
              <li><a href="#" className="hover:text-gray-700">문의</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">법적 고지</h4>
            <ul className="space-y-2 text-sm text-gray-500">
              <li><a href="#" className="hover:text-gray-700">이용약관</a></li>
              <li><a href="#" className="hover:text-gray-700">개인정보처리방침</a></li>
              <li><a href="#" className="hover:text-gray-700">쿠키 정책</a></li>
            </ul>
          </div>
        </div>
        <div className="mt-12 pt-8 border-t border-gray-100 text-center text-sm text-gray-400">
          © 2025 SupportAI. All rights reserved.
        </div>
      </div>
    </footer>
  );
}

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <Navbar />
      <HeroSection />
      <FeaturesSection />
      <PricingSection />
      <CTASection />
      <Footer />
    </main>
  );
}
