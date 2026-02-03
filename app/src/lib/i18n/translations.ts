export const translations = {
  ko: {
    // Common
    common: {
      loading: "로딩 중...",
      error: "오류가 발생했습니다",
      save: "저장",
      cancel: "취소",
      delete: "삭제",
      edit: "수정",
      search: "검색",
      back: "뒤로",
      next: "다음",
      previous: "이전",
      confirm: "확인",
      close: "닫기",
      viewAll: "전체 보기",
    },

    // Navigation
    nav: {
      features: "기능",
      pricing: "요금제",
      demo: "데모",
      dashboard: "대시보드",
      login: "로그인",
      signup: "회원가입",
    },

    // Landing Page
    landing: {
      hero: {
        badge: "새로운 GPT-4o 기반 엔진 출시",
        title: "AI 고객지원 플랫폼으로",
        titleHighlight: "고객 만족도를 극대화",
        titleSuffix: "하세요",
        subtitle: "24시간 자동 응답, 다국어 지원, 실시간 분석까지. AI가 고객지원의 새로운 기준을 만듭니다.",
        ctaPrimary: "무료 데모 체험하기",
        ctaSecondary: "위젯 미리보기",
        noCard: "신용카드 불필요",
        quickSetup: "5분 내 설정 완료",
        freeTrial: "14일 무료 체험",
      },
      stats: {
        satisfaction: "고객 만족도",
        responseTime: "평균 응답 시간",
        languages: "지원 언어",
        activeUsers: "활성 사용자",
      },
      features: {
        title: "더 똑똑한 고객지원,",
        titleHighlight: "더 행복한 고객",
        subtitle: "AI 기술로 고객지원의 모든 과정을 자동화하고 최적화합니다",
        autoResponse: {
          title: "24/7 자동 응답",
          description: "AI가 고객 문의에 24시간 즉각 대응합니다. 영업 시간에 구애받지 않는 빈틈없는 고객 경험을 제공하세요.",
        },
        multilingual: {
          title: "다국어 지원",
          description: "50개 이상의 언어를 자동으로 감지하고 번역합니다. 글로벌 고객에게 모국어로 서비스를 제공하세요.",
        },
        analytics: {
          title: "실시간 분석",
          description: "고객 만족도, 응답 시간, 자주 묻는 질문을 실시간으로 분석합니다. 데이터 기반 의사결정을 지원합니다.",
        },
        easySetup: {
          title: "간편한 설치",
          description: "코드 한 줄이면 기존 웹사이트에 즉시 통합됩니다. 별도의 개발 리소스 없이 5분 만에 설정을 완료하세요.",
        },
        smartLearning: {
          title: "스마트 학습",
          description: "고객과의 대화에서 지속적으로 학습하여 응답 품질이 향상됩니다. 시간이 지날수록 더 똑똑해지는 AI입니다.",
        },
        security: {
          title: "기업급 보안",
          description: "엔드투엔드 암호화, SOC 2 인증, GDPR 준수. 고객 데이터의 안전을 최우선으로 보장합니다.",
        },
      },
      pricing: {
        title: "합리적인 요금제",
        subtitle: "비즈니스 규모에 맞는 플랜을 선택하세요. 언제든 업그레이드할 수 있습니다.",
        popular: "가장 인기 있는 플랜",
        free: {
          name: "무료",
          price: "₩0",
          period: "/월",
          description: "소규모 팀이 시작하기에 딱 좋은 플랜",
          cta: "무료로 시작",
        },
        pro: {
          name: "프로",
          price: "₩49,000",
          period: "/월",
          description: "성장하는 비즈니스를 위한 강력한 도구",
          cta: "14일 무료 체험",
        },
        enterprise: {
          name: "엔터프라이즈",
          price: "맞춤 견적",
          period: "",
          description: "대규모 조직을 위한 맞춤형 솔루션",
          cta: "영업팀 문의",
        },
      },
      cta: {
        title: "지금 바로 시작하세요",
        subtitle: "5분 만에 AI 고객지원을 도입하고, 고객 만족도를 높여보세요. 첫 14일은 무료입니다.",
      },
    },

    // Demo Page
    demo: {
      title: "AI 채팅 데모",
      subtitle: "실시간 AI 고객지원 체험 — 이커머스 시나리오",
      backendConnected: "AI 백엔드에 연결되었습니다 — 실시간 RAG 기반 응답",
      inputPlaceholder: "메시지를 입력하세요...",
      quickQuestions: ["배송 조회", "반품 신청", "결제 오류", "쿠폰 사용법"],
      infoCards: {
        instant: {
          title: "즉각 응답",
          description: "평균 0.3초 내 AI 자동 응답",
        },
        context: {
          title: "컨텍스트 이해",
          description: "대화 맥락을 파악하여 정확한 답변",
        },
        escalation: {
          title: "상담원 연결",
          description: "필요 시 실제 상담원에게 자동 전환",
        },
      },
    },

    // Dashboard
    dashboard: {
      title: "대시보드",
      subtitle: "오늘의 고객지원 현황을 한눈에 확인하세요",
      tabs: {
        overview: "개요",
        analytics: "분석",
        conversations: "대화",
      },
      stats: {
        totalConversations: "총 대화 수",
        avgResponseTime: "평균 응답 시간",
        satisfaction: "고객 만족도",
        activeChats: "활성 채팅",
      },
      recentConversations: "최근 대화",
      weeklyTrends: "주간 대화 추이",
      categoryDistribution: "문의 카테고리 분포",
    },

    // Footer
    footer: {
      tagline: "AI 기반 차세대 고객지원 플랫폼",
      product: "제품",
      company: "회사",
      legal: "법적 고지",
      about: "소개",
      blog: "블로그",
      careers: "채용",
      contact: "문의",
      terms: "이용약관",
      privacy: "개인정보처리방침",
      cookies: "쿠키 정책",
      copyright: "© 2025 SupportAI. All rights reserved.",
    },

    // Status
    status: {
      online: "온라인",
      offline: "오프라인",
      backendConnected: "백엔드 연결됨",
      demoMode: "데모 모드",
      inProgress: "진행중",
      completed: "완료",
      escalated: "상담원 전환",
    },
  },

  en: {
    // Common
    common: {
      loading: "Loading...",
      error: "An error occurred",
      save: "Save",
      cancel: "Cancel",
      delete: "Delete",
      edit: "Edit",
      search: "Search",
      back: "Back",
      next: "Next",
      previous: "Previous",
      confirm: "Confirm",
      close: "Close",
      viewAll: "View all",
    },

    // Navigation
    nav: {
      features: "Features",
      pricing: "Pricing",
      demo: "Demo",
      dashboard: "Dashboard",
      login: "Login",
      signup: "Sign up",
    },

    // Landing Page
    landing: {
      hero: {
        badge: "New GPT-4o powered engine",
        title: "Maximize customer satisfaction with",
        titleHighlight: "AI Customer Support",
        titleSuffix: "",
        subtitle: "24/7 automated responses, multilingual support, real-time analytics. AI sets the new standard for customer support.",
        ctaPrimary: "Try Free Demo",
        ctaSecondary: "Preview Widget",
        noCard: "No credit card required",
        quickSetup: "5-minute setup",
        freeTrial: "14-day free trial",
      },
      stats: {
        satisfaction: "Customer Satisfaction",
        responseTime: "Avg Response Time",
        languages: "Languages",
        activeUsers: "Active Users",
      },
      features: {
        title: "Smarter Customer Support,",
        titleHighlight: "Happier Customers",
        subtitle: "Automate and optimize every aspect of customer support with AI technology",
        autoResponse: {
          title: "24/7 Auto Response",
          description: "AI responds to customer inquiries around the clock. Provide seamless customer experience without business hour constraints.",
        },
        multilingual: {
          title: "Multilingual Support",
          description: "Automatically detect and translate 50+ languages. Serve global customers in their native language.",
        },
        analytics: {
          title: "Real-time Analytics",
          description: "Analyze customer satisfaction, response times, and FAQs in real-time. Enable data-driven decision making.",
        },
        easySetup: {
          title: "Easy Installation",
          description: "Integrate with your existing website with just one line of code. Complete setup in 5 minutes without additional development resources.",
        },
        smartLearning: {
          title: "Smart Learning",
          description: "Continuously learn from customer conversations to improve response quality. AI that gets smarter over time.",
        },
        security: {
          title: "Enterprise Security",
          description: "End-to-end encryption, SOC 2 certified, GDPR compliant. Customer data safety is our top priority.",
        },
      },
      pricing: {
        title: "Fair Pricing",
        subtitle: "Choose a plan that fits your business. Upgrade anytime.",
        popular: "Most Popular",
        free: {
          name: "Free",
          price: "$0",
          period: "/mo",
          description: "Perfect for small teams getting started",
          cta: "Get Started Free",
        },
        pro: {
          name: "Pro",
          price: "$49",
          period: "/mo",
          description: "Powerful tools for growing businesses",
          cta: "14-day Free Trial",
        },
        enterprise: {
          name: "Enterprise",
          price: "Custom",
          period: "",
          description: "Custom solutions for large organizations",
          cta: "Contact Sales",
        },
      },
      cta: {
        title: "Get Started Today",
        subtitle: "Implement AI customer support in 5 minutes and boost customer satisfaction. First 14 days are free.",
      },
    },

    // Demo Page
    demo: {
      title: "AI Chat Demo",
      subtitle: "Experience real-time AI customer support — E-commerce scenario",
      backendConnected: "Connected to AI backend — Real-time RAG-based responses",
      inputPlaceholder: "Type a message...",
      quickQuestions: ["Track order", "Return request", "Payment error", "How to use coupons"],
      infoCards: {
        instant: {
          title: "Instant Response",
          description: "AI auto-response within 0.3 seconds",
        },
        context: {
          title: "Context Understanding",
          description: "Accurate answers by understanding conversation context",
        },
        escalation: {
          title: "Agent Handoff",
          description: "Automatic transfer to human agents when needed",
        },
      },
    },

    // Dashboard
    dashboard: {
      title: "Dashboard",
      subtitle: "View today's customer support status at a glance",
      tabs: {
        overview: "Overview",
        analytics: "Analytics",
        conversations: "Conversations",
      },
      stats: {
        totalConversations: "Total Conversations",
        avgResponseTime: "Avg Response Time",
        satisfaction: "Customer Satisfaction",
        activeChats: "Active Chats",
      },
      recentConversations: "Recent Conversations",
      weeklyTrends: "Weekly Conversation Trends",
      categoryDistribution: "Inquiry Category Distribution",
    },

    // Footer
    footer: {
      tagline: "Next-gen AI-powered customer support platform",
      product: "Product",
      company: "Company",
      legal: "Legal",
      about: "About",
      blog: "Blog",
      careers: "Careers",
      contact: "Contact",
      terms: "Terms of Service",
      privacy: "Privacy Policy",
      cookies: "Cookie Policy",
      copyright: "© 2025 SupportAI. All rights reserved.",
    },

    // Status
    status: {
      online: "Online",
      offline: "Offline",
      backendConnected: "Backend connected",
      demoMode: "Demo mode",
      inProgress: "In Progress",
      completed: "Completed",
      escalated: "Escalated",
    },
  },
} as const;

export type Language = keyof typeof translations;
export type TranslationKey = keyof typeof translations.ko;
