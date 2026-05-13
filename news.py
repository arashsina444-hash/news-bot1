import feedparser

RSS_URL = "https://feeds.feedburner.com/reuters/technologyNews"

def get_news():
    feed = feedparser.parse(RSS_URL)

    with open("news.txt", "w", encoding="utf-8") as f:
        f.write("Latest Tech News\n\n")

        for entry in feed.entries[:10]:
            f.write(entry.title + "\n")
            f.write(entry.link + "\n")
            f.write("---------------------\n")

if __name__ == "__main__":
    get_news()
