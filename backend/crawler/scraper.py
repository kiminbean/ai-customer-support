"""
웹 크롤러 — 비동기 웹 페이지 수집기

httpx(비동기) + BeautifulSoup4로 웹사이트를 크롤링하여
FAQ, 도움말, 상품정보 등 고객지원 콘텐츠를 수집한다.

기능:
- robots.txt 준수
- 동일 도메인 제한
- URL 패턴 필터링 (include/exclude)
- 속도 제한 (1req/sec)
- 설정 가능한 크롤링 깊이 및 최대 페이지 수
"""

from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup


# ── 데이터 모델 ────────────────────────────────────────────


@dataclass
class CrawlConfig:
    """크롤링 설정"""

    url: str                                        # 시작 URL
    max_depth: int = 2                              # 크롤링 깊이
    max_pages: int = 50                             # 최대 페이지 수
    same_domain_only: bool = True                   # 같은 도메인만 크롤링
    include_patterns: list[str] = field(default_factory=list)   # 포함할 URL 패턴
    exclude_patterns: list[str] = field(default_factory=list)   # 제외할 URL 패턴
    extract_mode: str = "auto"                      # auto | faq | all
    request_delay: float = 1.0                      # 요청 간 딜레이 (초)
    timeout: float = 15.0                           # 요청 타임아웃 (초)
    user_agent: str = "AICustomerSupport-Crawler/1.0"


@dataclass
class CrawledPage:
    """크롤링된 단일 페이지"""

    url: str
    title: str = ""
    html: str = ""
    text_content: str = ""
    headings: list[dict] = field(default_factory=list)       # [{level, text}]
    paragraphs: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)           # 발견된 링크
    meta_description: str = ""
    status_code: int = 0
    crawl_depth: int = 0
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "text_content": self.text_content[:500] + ("..." if len(self.text_content) > 500 else ""),
            "headings": self.headings,
            "meta_description": self.meta_description,
            "status_code": self.status_code,
            "crawl_depth": self.crawl_depth,
            "links_found": len(self.links),
            "error": self.error,
        }


# ── 크롤러 본체 ────────────────────────────────────────────


class WebCrawler:
    """비동기 웹 크롤러"""

    def __init__(self, config: CrawlConfig):
        self.config = config
        self.visited: set[str] = set()
        self.pages: list[CrawledPage] = []
        self.queue: list[tuple[str, int]] = []      # (url, depth)
        self.robot_parser: RobotFileParser | None = None
        self._base_domain: str = ""
        self._last_request_time: float = 0.0

        # 콜백: 진행 상황 보고
        self.on_progress: Callable[[str, int, int], None] | None = None

    # ── public ──

    async def crawl(self) -> list[CrawledPage]:
        """크롤링 실행 → 수집된 페이지 목록 반환"""
        parsed = urlparse(self.config.url)
        self._base_domain = parsed.netloc

        # robots.txt 로드
        await self._load_robots(parsed.scheme, parsed.netloc)

        # 시작 URL 큐에 추가
        self.queue.append((self._normalize_url(self.config.url), 0))

        async with httpx.AsyncClient(
            headers={"User-Agent": self.config.user_agent},
            timeout=httpx.Timeout(self.config.timeout),
            follow_redirects=True,
            verify=False,  # 자체 서명 인증서 허용
        ) as client:
            while self.queue and len(self.pages) < self.config.max_pages:
                url, depth = self.queue.pop(0)

                if url in self.visited:
                    continue
                if depth > self.config.max_depth:
                    continue
                if not self._is_allowed(url):
                    continue

                self.visited.add(url)

                # 속도 제한
                await self._rate_limit()

                # 페이지 크롤링
                page = await self._fetch_page(client, url, depth)
                if page:
                    self.pages.append(page)

                    # 진행 보고
                    if self.on_progress:
                        self.on_progress(url, len(self.pages), self.config.max_pages)

                    # 발견된 링크를 큐에 추가
                    if depth < self.config.max_depth:
                        for link in page.links:
                            if link not in self.visited:
                                self.queue.append((link, depth + 1))

        return self.pages

    # ── private ──

    async def _load_robots(self, scheme: str, netloc: str) -> None:
        """robots.txt 파싱"""
        robots_url = f"{scheme}://{netloc}/robots.txt"
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": self.config.user_agent},
                timeout=httpx.Timeout(5.0),
                verify=False,
            ) as client:
                resp = await client.get(robots_url)
                if resp.status_code == 200:
                    self.robot_parser = RobotFileParser()
                    self.robot_parser.parse(resp.text.splitlines())
        except Exception:
            # robots.txt를 가져올 수 없으면 모두 허용
            self.robot_parser = None

    def _is_allowed(self, url: str) -> bool:
        """URL이 크롤링 가능한지 판단"""
        parsed = urlparse(url)

        # 같은 도메인만
        if self.config.same_domain_only and parsed.netloc != self._base_domain:
            return False

        # robots.txt 체크
        if self.robot_parser:
            try:
                if not self.robot_parser.can_fetch(self.config.user_agent, url):
                    return False
            except Exception:
                pass

        path = parsed.path.lower()

        # 제외 패턴
        default_excludes = [
            "/login", "/admin", "/cart", "/checkout", "/account",
            "/wp-admin", "/wp-login", ".css", ".js", ".jpg", ".png",
            ".gif", ".svg", ".pdf", ".zip", ".exe",
        ]
        all_excludes = default_excludes + [p.lower() for p in self.config.exclude_patterns]
        for pattern in all_excludes:
            if pattern in path:
                return False

        # 포함 패턴 (비어 있으면 모두 허용)
        if self.config.include_patterns:
            include_lower = [p.lower() for p in self.config.include_patterns]
            # 시작 URL은 항상 허용
            if url == self._normalize_url(self.config.url):
                return True
            return any(p in path for p in include_lower)

        return True

    async def _rate_limit(self) -> None:
        """요청 간 딜레이 유지"""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self.config.request_delay:
            await asyncio.sleep(self.config.request_delay - elapsed)
        self._last_request_time = time.monotonic()

    async def _fetch_page(
        self, client: httpx.AsyncClient, url: str, depth: int
    ) -> CrawledPage | None:
        """단일 페이지 가져오기 및 파싱"""
        page = CrawledPage(url=url, crawl_depth=depth)

        try:
            resp = await client.get(url)
            page.status_code = resp.status_code

            if resp.status_code != 200:
                page.error = f"HTTP {resp.status_code}"
                return page

            # HTML이 아닌 콘텐츠 건너뛰기
            content_type = resp.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return None

            page.html = resp.text
            soup = BeautifulSoup(resp.text, "lxml")

            # 제목
            title_tag = soup.find("title")
            page.title = title_tag.get_text(strip=True) if title_tag else ""

            # 메타 설명
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                page.meta_description = meta_desc["content"]

            # 헤딩
            for level in range(1, 7):
                for h in soup.find_all(f"h{level}"):
                    text = h.get_text(strip=True)
                    if text:
                        page.headings.append({"level": level, "text": text})

            # 본문 텍스트 (불필요한 태그 제거)
            for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                tag.decompose()

            # 단락
            for p in soup.find_all("p"):
                text = p.get_text(strip=True)
                if text and len(text) > 20:
                    page.paragraphs.append(text)

            page.text_content = soup.get_text(separator="\n", strip=True)
            # 연속 공백/줄바꿈 정리
            page.text_content = re.sub(r"\n{3,}", "\n\n", page.text_content)

            # 링크 수집
            page.links = self._extract_links(soup, url)

            return page

        except httpx.TimeoutException:
            page.error = "타임아웃"
            return page
        except httpx.ConnectError:
            page.error = "연결 실패"
            return page
        except Exception as e:
            page.error = f"오류: {str(e)[:100]}"
            return page

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        """페이지에서 링크 추출"""
        links: list[str] = []
        seen: set[str] = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()

            # 빈 링크, 앵커, javascript 건너뛰기
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue
            if href.startswith("mailto:") or href.startswith("tel:"):
                continue

            # 절대 URL로 변환
            absolute = urljoin(base_url, href)
            normalized = self._normalize_url(absolute)

            if normalized not in seen:
                seen.add(normalized)
                links.append(normalized)

        return links

    @staticmethod
    def _normalize_url(url: str) -> str:
        """URL 정규화 (쿼리 파라미터 제거, 끝 슬래시 통일)"""
        parsed = urlparse(url)
        # fragment 제거, 쿼리 유지
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        # 끝 슬래시 제거 (루트 제외)
        if normalized.endswith("/") and parsed.path != "/":
            normalized = normalized.rstrip("/")
        return normalized
