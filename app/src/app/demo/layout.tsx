import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "데모 체험 - AI 채팅봇 무료 테스트",
  description: "SupportAI 챗봇을 지금 바로 체험해보세요. 회원가입 없이 AI 고객지원의 강력한 기능을 경험할 수 있습니다.",
  openGraph: {
    title: "데모 체험 | SupportAI",
    description: "SupportAI 챗봇을 지금 바로 체험해보세요. 회원가입 없이 AI 고객지원의 강력한 기능을 경험할 수 있습니다.",
  },
};

export default function DemoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
