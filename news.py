import feedparser

RSS_URL = "https://feeds.feedburner.com/reuters/technologyNews"

def get_news():
    feed = feedparser.parse(RSS_URL)
    print("Latest Reuters Technology News:")
    for entry in feed.entries[:5]:
        print(entry.title)
        print(entry.link)
        print("-" * 30)

if __name__ == "__main__":
    get_news()
