import os
import time
from openai import OpenAI

def read_file(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def try_request(base_url, api_key, news_content):
    client = OpenAI(base_url=base_url, api_key=api_key)

    for attempt in range(1, 4):
        print(f"🔁 [{base_url}] Attempt {attempt}/3 ...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Rewrite the news for Rubika posts."},
                    {"role": "user", "content": news_content},
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ ERROR on {base_url} (attempt {attempt}): {e}")
            time.sleep(2)

    return None


def main():
    print("🚀 Starting AI Generation...")

    api_key = os.getenv("GAPGPT_API_KEY")
    if not api_key:
        write_file("rubika_posts.txt", "API KEY ERROR")
        return

    news = read_file("news.txt")
    if not news:
        write_file("rubika_posts.txt", "NO NEWS PROVIDED")
        return

    urls = [
        "https://api.gapgpt.app/v1",
        "https://api.gapgpt.com/v1"
    ]

    result = None

    for url in urls:
        print(f"🌐 Trying API endpoint: {url}")
        result = try_request(url, api_key, news)

        if result:  
            break  

    if not result:
        print("❌ Both endpoints failed!")
        write_file("rubika_posts.txt", "GAPGPT FAILED")
        return

    write_file("rubika_posts.txt", result)
    print("🎉 DONE. Output saved.")

if __name__ == "__main__":
    main()
