"""Thu thập tin tức từ RSS - tập trung thị trường vàng Việt Nam."""
import re
from datetime import datetime, timedelta, timezone
from html import unescape

import feedparser

from config import GOLD_KEYWORDS, MAX_AGE_HOURS, RSS_SOURCES


def _clean_html(text: str) -> str:
    """Loại bỏ thẻ HTML."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return " ".join(text.split()).strip()


def _is_gold_related(title: str, summary: str) -> bool:
    """Kiểm tra tin có liên quan vàng không."""
    combined = f"{title} {summary}".lower()
    return any(kw.lower() in combined for kw in GOLD_KEYWORDS)


def _parse_date(entry) -> datetime | None:
    """Parse ngày publish từ RSS entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    return None


def _is_recent(pub_date: datetime | None) -> bool:
    """Kiểm tra tin không quá 48h."""
    if not pub_date:
        return True
    cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
    return pub_date >= cutoff


def fetch_news() -> list[dict]:
    """
    Lấy tin từ RSS, lọc theo từ khóa vàng, loại tin cũ.
    Trả về danh sách tin đã sắp xếp theo thời gian (mới nhất trước).
    """
    all_news = []
    seen_urls = set()

    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(
                source["url"],
                request_headers={"User-Agent": "GoldNewsBot/1.0"},
            )
        except Exception:
            continue

        for entry in feed.entries:
            url = entry.get("link", "")
            if not url or url in seen_urls:
                continue

            title = _clean_html(entry.get("title", ""))
            summary = _clean_html(entry.get("summary", "")) or _clean_html(
                entry.get("description", "")
            )

            if not _is_gold_related(title, summary):
                continue

            pub_date = _parse_date(entry)
            if not _is_recent(pub_date):
                continue

            seen_urls.add(url)
            all_news.append(
                {
                    "title": title,
                    "summary": summary[:300] if summary else "",
                    "url": url,
                    "source": source["name"],
                    "published": pub_date.isoformat() if pub_date else "",
                }
            )

    # Sắp xếp mới nhất trước
    all_news.sort(
        key=lambda x: x["published"] or "",
        reverse=True,
    )
    return all_news
