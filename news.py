import feedparser
import re
from html import unescape

RSS_URL = "https://feeds.feedburner.com/reuters/technologyNews"

def strip_html(text: str) -> str:
    # حذف تگ‌های HTML ساده
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = unescape(text)
    # یکدست کردن فاصله‌ها
    text = re.sub(r"\s+", " ", text).strip()
    return text

feed = feedparser.parse(RSS_URL)

with open("news.txt", "w", encoding="utf-8") as f:
    f.write("Latest Tech News\n\n")

    if not feed.entries:
        f.write("No news found or RSS link is broken.\n")
    else:
        for entry in feed.entries:
            title = (entry.title or "").strip()
            link = (entry.link or "").strip()

            # تلاش برای گرفتن خلاصه
            summary = ""
            if hasattr(entry, "summary") and entry.summary:
                summary = strip_html(entry.summary)
            elif hasattr(entry, "description") and entry.description:
                summary = strip_html(entry.description)
            elif hasattr(entry, "summary_detail") and entry.summary_detail:
                summary = strip_html(getattr(entry.summary_detail, "value", "") or "")
            else:
                summary = ""

            f.write(f"Title: {title}\n")
            if summary:
                # برای اینکه فایل خیلی بزرگ نشه، خلاصه را کوتاه می‌کنیم
                f.write(f"Summary: {summary[:500]}\n")
            else:
                f.write("Summary: (RSS did not provide summary)\n")

            f.write(f"Link: {link}\n")
            f.write("-" * 60 + "\n")

print("News saved to news.txt successfully.")
