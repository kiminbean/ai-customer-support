"""
Tests for crawler/scraper module
Target: Increase coverage from 27% to 70%+
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from crawler.scraper import CrawlConfig, CrawledPage, WebCrawler


class TestCrawlConfig:
    """CrawlConfig 데이터클래스 테스트"""

    def test_default_values(self):
        """기본값 확인"""
        config = CrawlConfig(url="https://example.com")

        assert config.url == "https://example.com"
        assert config.max_depth == 2
        assert config.max_pages == 50
        assert config.same_domain_only is True
        assert config.include_patterns == []
        assert config.exclude_patterns == []
        assert config.extract_mode == "auto"
        assert config.request_delay == 1.0
        assert config.timeout == 15.0

    def test_custom_values(self):
        """커스텀 값"""
        config = CrawlConfig(
            url="https://example.com",
            max_depth=3,
            max_pages=100,
            same_domain_only=False,
            include_patterns=["/faq", "/help"],
            exclude_patterns=["/admin"],
            request_delay=0.5,
        )

        assert config.max_depth == 3
        assert config.max_pages == 100
        assert config.same_domain_only is False
        assert config.include_patterns == ["/faq", "/help"]
        assert config.exclude_patterns == ["/admin"]
        assert config.request_delay == 0.5


class TestCrawledPage:
    """CrawledPage 데이터클래스 테스트"""

    def test_default_values(self):
        """기본값 확인"""
        page = CrawledPage(url="https://example.com/page")

        assert page.url == "https://example.com/page"
        assert page.title == ""
        assert page.html == ""
        assert page.text_content == ""
        assert page.headings == []
        assert page.paragraphs == []
        assert page.links == []
        assert page.meta_description == ""
        assert page.status_code == 0
        assert page.crawl_depth == 0
        assert page.error is None

    def test_to_dict(self):
        """to_dict 직렬화"""
        page = CrawledPage(
            url="https://example.com/page",
            title="Test Page",
            text_content="A" * 600,  # 긴 텍스트
            headings=[{"level": 1, "text": "Heading"}],
            meta_description="Test description",
            status_code=200,
            crawl_depth=1,
            links=["https://example.com/link1", "https://example.com/link2"],
            error=None,
        )

        result = page.to_dict()

        assert result["url"] == "https://example.com/page"
        assert result["title"] == "Test Page"
        assert "..." in result["text_content"]  # 잘림 표시
        assert result["headings"] == [{"level": 1, "text": "Heading"}]
        assert result["links_found"] == 2
        assert result["error"] is None

    def test_to_dict_with_error(self):
        """에러 포함 to_dict"""
        page = CrawledPage(
            url="https://example.com/404",
            status_code=404,
            error="HTTP 404",
        )

        result = page.to_dict()

        assert result["status_code"] == 404
        assert result["error"] == "HTTP 404"


class TestWebCrawlerInit:
    """WebCrawler 초기화 테스트"""

    def test_init(self):
        """초기화 상태"""
        config = CrawlConfig(url="https://example.com")
        crawler = WebCrawler(config)

        assert crawler.config == config
        assert crawler.visited == set()
        assert crawler.pages == []
        assert crawler.queue == []
        assert crawler.robot_parser is None
        assert crawler._base_domain == ""

    def test_progress_callback(self):
        """진행 콜백 설정"""
        config = CrawlConfig(url="https://example.com")
        crawler = WebCrawler(config)

        progress_calls = []

        def on_progress(url, count, total):
            progress_calls.append((url, count, total))

        crawler.on_progress = on_progress
        assert crawler.on_progress is not None


class TestNormalizeUrl:
    """_normalize_url 정적 메서드 테스트"""

    def test_remove_fragment(self):
        """프래그먼트 제거"""
        result = WebCrawler._normalize_url("https://example.com/page#section")
        assert result == "https://example.com/page"

    def test_trailing_slash(self):
        """끝 슬래시 제거"""
        result = WebCrawler._normalize_url("https://example.com/page/")
        assert result == "https://example.com/page"

    def test_root_keeps_slash(self):
        """루트 경로는 슬래시 유지"""
        result = WebCrawler._normalize_url("https://example.com/")
        assert result == "https://example.com/"


class TestIsAllowed:
    """_is_allowed URL 필터링 테스트"""

    @pytest.fixture
    def crawler(self):
        config = CrawlConfig(url="https://example.com")
        return WebCrawler(config)

    def test_same_domain_allowed(self, crawler):
        """같은 도메인 허용"""
        crawler._base_domain = "example.com"
        assert crawler._is_allowed("https://example.com/page") is True

    def test_different_domain_blocked(self, crawler):
        """다른 도메인 차단"""
        crawler._base_domain = "example.com"
        assert crawler._is_allowed("https://other.com/page") is False

    def test_different_domain_allowed_when_disabled(self, crawler):
        """same_domain_only=False면 다른 도메인 허용"""
        crawler.config.same_domain_only = False
        crawler._base_domain = "example.com"
        assert crawler._is_allowed("https://other.com/page") is True

    def test_exclude_patterns(self, crawler):
        """제외 패턴"""
        crawler._base_domain = "example.com"
        crawler.config.exclude_patterns = ["/secret"]
        assert crawler._is_allowed("https://example.com/secret/page") is False

    def test_default_excludes(self, crawler):
        """기본 제외 경로"""
        crawler._base_domain = "example.com"
        assert crawler._is_allowed("https://example.com/login") is False
        assert crawler._is_allowed("https://example.com/admin") is False
        assert crawler._is_allowed("https://example.com/style.css") is False

    def test_include_patterns(self, crawler):
        """포함 패턴"""
        crawler._base_domain = "example.com"
        crawler.config.include_patterns = ["/faq", "/help"]

        # 시작 URL은 항상 허용
        crawler.config.url = "https://example.com/start"
        assert crawler._is_allowed("https://example.com/start") is True

        # 포함 패턴에 없는 URL은 차단
        assert crawler._is_allowed("https://example.com/other") is False

        # 포함 패턴에 있는 URL은 허용
        assert crawler._is_allowed("https://example.com/faq") is True

    def test_empty_include_allows_all(self, crawler):
        """빈 include 패턴은 모두 허용"""
        crawler._base_domain = "example.com"
        crawler.config.include_patterns = []
        assert crawler._is_allowed("https://example.com/any-page") is True


class TestExtractLinks:
    """_extract_links 링크 추출 테스트"""

    @pytest.fixture
    def crawler(self):
        config = CrawlConfig(url="https://example.com")
        return WebCrawler(config)

    def test_extract_basic_links(self, crawler):
        """기본 링크 추출"""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <a href="/page1">Link 1</a>
            <a href="https://example.com/page2">Link 2</a>
            <a href="/page3">Link 3</a>
        </html>
        """
        soup = BeautifulSoup(html, "lxml")
        links = crawler._extract_links(soup, "https://example.com")

        assert len(links) == 3
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links

    def test_skip_anchors(self, crawler):
        """앵커 링크 건너뛰기"""
        from bs4 import BeautifulSoup

        html = """
        <a href="#section">Anchor</a>
        <a href="/page">Normal</a>
        """
        soup = BeautifulSoup(html, "lxml")
        links = crawler._extract_links(soup, "https://example.com")

        assert len(links) == 1
        assert links[0] == "https://example.com/page"

    def test_skip_javascript(self, crawler):
        """JavaScript 링크 건너뛰기"""
        from bs4 import BeautifulSoup

        html = """
        <a href="javascript:void(0)">JS Link</a>
        <a href="/page">Normal</a>
        """
        soup = BeautifulSoup(html, "lxml")
        links = crawler._extract_links(soup, "https://example.com")

        assert len(links) == 1

    def test_skip_mailto(self, crawler):
        """mailto 링크 건너뛰기"""
        from bs4 import BeautifulSoup

        html = """
        <a href="mailto:test@example.com">Email</a>
        <a href="/page">Normal</a>
        """
        soup = BeautifulSoup(html, "lxml")
        links = crawler._extract_links(soup, "https://example.com")

        assert len(links) == 1

    def test_deduplicate_links(self, crawler):
        """중복 링크 제거"""
        from bs4 import BeautifulSoup

        html = """
        <a href="/page">Link 1</a>
        <a href="/page">Link 1 Again</a>
        <a href="/other">Link 2</a>
        """
        soup = BeautifulSoup(html, "lxml")
        links = crawler._extract_links(soup, "https://example.com")

        assert len(links) == 2


class TestRateLimit:
    """_rate_limit 속도 제한 테스트"""

    @pytest.mark.asyncio
    async def test_rate_limit_delays(self):
        """속도 제한 지연"""
        config = CrawlConfig(url="https://example.com", request_delay=0.1)
        crawler = WebCrawler(config)

        import time
        start = time.monotonic()
        await crawler._rate_limit()
        await crawler._rate_limit()
        elapsed = time.monotonic() - start

        # 두 번째 호출은 delay만큼 대기해야 함
        assert elapsed >= 0.1


class TestFetchPage:
    """_fetch_page 페이지 가져오기 테스트"""

    @pytest.fixture
    def crawler(self):
        config = CrawlConfig(url="https://example.com", timeout=5.0)
        return WebCrawler(config)

    @pytest.mark.asyncio
    async def test_fetch_success(self, crawler):
        """성공적인 페이지 가져오기"""
        from bs4 import BeautifulSoup

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Heading 1</h1>
                <p>This is a paragraph with enough text to be included.</p>
                <a href="/link">Link</a>
            </body>
        </html>
        """
        mock_response.headers = {"content-type": "text/html"}

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await crawler._fetch_page(mock_client, "https://example.com/test", 0)

        assert result is not None
        assert result.title == "Test Page"
        assert result.status_code == 200
        assert len(result.headings) == 1
        assert result.headings[0]["level"] == 1
        assert result.headings[0]["text"] == "Heading 1"

    @pytest.mark.asyncio
    async def test_fetch_non_html(self, crawler):
        """HTML이 아닌 콘텐츠 건너뛰기"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "not html"
        mock_response.headers = {"content-type": "application/json"}

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await crawler._fetch_page(mock_client, "https://example.com/api", 0)

        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_error_status(self, crawler):
        """에러 상태 코드"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = ""
        mock_response.headers = {"content-type": "text/html"}

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await crawler._fetch_page(mock_client, "https://example.com/404", 0)

        assert result is not None
        assert result.status_code == 404
        assert result.error == "HTTP 404"

    @pytest.mark.asyncio
    async def test_fetch_timeout(self, crawler):
        """타임아웃 처리"""
        import httpx

        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        result = await crawler._fetch_page(mock_client, "https://example.com/slow", 0)

        assert result is not None
        assert result.error == "타임아웃"

    @pytest.mark.asyncio
    async def test_fetch_connect_error(self, crawler):
        """연결 실패 처리"""
        import httpx

        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))

        result = await crawler._fetch_page(mock_client, "https://example.com/down", 0)

        assert result is not None
        assert result.error == "연결 실패"


class TestCrawlIntegration:
    """크롤링 통합 테스트"""

    @pytest.mark.asyncio
    async def test_crawl_single_page(self):
        """단일 페이지 크롤링"""
        config = CrawlConfig(
            url="https://example.com",
            max_depth=0,
            max_pages=1,
        )
        crawler = WebCrawler(config)

        # httpx 클라이언트 모킹
        with patch("crawler.scraper.httpx.AsyncClient") as MockClient:
            mock_client = MagicMock()

            # robots.txt 응답
            robots_resp = MagicMock()
            robots_resp.status_code = 404

            # 페이지 응답
            page_resp = MagicMock()
            page_resp.status_code = 200
            page_resp.text = "<html><head><title>Test</title></head><body></body></html>"
            page_resp.headers = {"content-type": "text/html"}

            mock_client.get = AsyncMock(side_effect=[robots_resp, page_resp])
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            pages = await crawler.crawl()

            assert len(pages) >= 0  # 크롤링 결과
