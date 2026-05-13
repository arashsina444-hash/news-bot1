import os
from openai import OpenAI

# دریافت کلیه متغیرهای محیطی برای اطمینان
api_key = os.getenv("GAPGPT_API_KEY")

if not api_key:
    print("❌ خطا: کلید API در Secrets یافت نشد. لطفاً تنظیمات GitHub Secrets را چک کنید.")
    exit(1)

client = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key=api_key
)

def generate_post(title, summary, link):
    try:
        prompt = f"""
این خبر را به یک پست جذاب برای کانال روبیکا تبدیل کن:
تیتر: {title}
خلاصه: {summary}
لینک منبع: {link}

قوانین:
- استفاده از ایموجی‌های مناسب
- لحن خبری و جذاب
- ذکر لینک منبع در انتها
"""
        response = client.chat.completions.create(
            model="gpt-chat-5.3-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ خطا در ارتباط با هوش مصنوعی: {str(e)}"

# بررسی وجود فایل ورودی
if not os.path.exists("news.txt"):
    print("❌ خطا: فایل news.txt پیدا نشد!")
    exit(1)

with open("news.txt", "r", encoding="utf-8") as f:
    content = f.read()

# جدا کردن اخبار بر اساس جداکننده -----
entries = [e.strip() for e in content.split("-----") if e.strip()]

processed_posts = []

print(f"🔍 در حال پردازش {len(entries)} خبر...")

for entry in entries:
    lines = entry.split("\n")
    if len(lines) >= 3:
        # پاکسازی متن خطوط (حذف پیشوندهای احتمالی)
        title = lines[0].replace("Title:", "").strip()
        summary = lines[1].replace("Summary:", "").strip()
        link = lines[2].replace("Link:", "").strip()
        
        print(f"✍️ در حال تولید پست برای: {title[:50]}...")
        post = generate_post(title, summary, link)
        processed_posts.append(post)

# ذخیره نهایی
with open("rubika_posts.txt", "w", encoding="utf-8") as f:
    for p in processed_posts:
        f.write(p + "\n\n" + "="*30 + "\n\n")

print("✅ عملیات با موفقیت تمام شد و فایل rubika_posts.txt ساخته شد.")
