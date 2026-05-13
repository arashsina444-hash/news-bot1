import os
from openai import OpenAI
import time

def read_file(path):
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    print("🚀 Starting AI Generation...")

    api_key = os.getenv("GAPGPT_API_KEY")
    if not api_key:
        print("❌ ERROR: GAPGPT_API_KEY is missing!")
        write_file("rubika_posts.txt", "API KEY ERROR")
        return

    client = OpenAI(
        base_url="https://api.gapgpt.app/v1",
        api_key=api_key
    )

    print("📄 Reading news.txt...")
    news_content = read_file("news.txt")
    if not news_content:
        print("❌ ERROR: news.txt is empty or missing.")
        write_file("rubika_posts.txt", "NO NEWS")
        return

    # Retry mechanism
    retries = 3
    response_text = None

    for attempt in range(1, retries + 1):
        print(f"🔁 Attempt {attempt}/{retries} ...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You rewrite news into Rubika format."},
                    {"role": "user", "content": news_content}
                ]
            )
            response_text = response.choices[0].message.content
            break

        except Exception as e:
            print(f"❌ ERROR (attempt {attempt}): {e}")
            time.sleep(2)

    if not response_text:
        print("❌ GAPGPT FAILED after all retries.")
        write_file("rubika_posts.txt", "GAPGPT ERROR")
        return

    print("📝 Writing output file...")
    write_file("rubika_posts.txt", response_text)

    print("🎉 DONE! File generated successfully.")

if __name__ == "__main__":
    main()
