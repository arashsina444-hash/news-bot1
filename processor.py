import os
from openai import OpenAI

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
        return

    # -------- تنظیم اتصال GAPGPT --------
    client = OpenAI(
        base_url="https://api.gapgpt.app/v1",
        api_key=api_key
    )
    # --------------------------------------

    print("📄 Reading news.txt...")
    news_content = read_file("news.txt")
    if not news_content:
        print("❌ ERROR: news.txt is empty or missing.")
        return

    print("🤖 Sending request to GAPGPT AI...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI that rewrites news into Rubika post format."},
                {"role": "user", "content": news_content}
            ]
        )
        final_text = response.choices[0].message.content
        print("✅ AI response received.")

    except Exception as e:
        print("❌ API ERROR:")
        print(e)
        return

    print("📝 Writing output to rubika_posts.txt ...")
    write_file("rubika_posts.txt", final_text)

    print("🎉 DONE! File generated successfully.")

if __name__ == "__main__":
    main()
