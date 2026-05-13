import os
import json
from openai import OpenAI

# Load API Key
api_key = os.getenv("GAPGPT_API_KEY")

if not api_key or len(api_key) < 10:
    print("❌ ERROR: GAPGPT_API_KEY not found or invalid.")
    exit(1)

client = OpenAI(api_key=api_key, base_url="https://api.gapgpt.com/v1")

# Check input file
if not os.path.exists("news.txt"):
    print("❌ ERROR: news.txt not found.")
    exit(1)

print("📄 Reading news.txt...")
with open("news.txt", "r", encoding="utf-8") as f:
    news_data = f.read()

if len(news_data.strip()) == 0:
    print("❌ ERROR: news.txt is empty!")
    exit(1)

print("🤖 Sending request to GAPGPT AI...")

try:
    prompt_text = f"""
تو یک ربات تولید پست روبیکا هستی.
این خلاصه خبرها را می‌گیری و برای هر خبر یک پست کامل، جذاب، روان و مناسب شبکه اجتماعی روبیکا تولید می‌کنی.
اگر خلاصه خیلی کوتاه بود، خودت با خلاقیت متن را گسترش بده.

خلاصه خبرها:
{news_data}

خروجی را فقط به صورت متن آماده برای انتشار بده.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional social media content generator."},
            {"role": "user", "content": prompt_text}
        ]
    )

    result = response.choices[0].message["content"]

except Exception as e:
    print("❌ AI API ERROR:")
    print(str(e))
    exit(1)

print("✍️ Writing output to rubika_posts.txt...")

with open("rubika_posts.txt", "w", encoding="utf-8") as f:
    f.write(result)

print("✅ rubika_posts.txt generated successfully!")
