import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key=os.getenv("GAPGPT_API_KEY")
)

def generate_post(title, summary, link):

    prompt = f"""
این خبر را تبدیل به یک پست کانال روبیکا کن.

تیتر خبر:
{title}

خلاصه:
{summary}

قوانین:
- متن فارسی روان
- حدود یک پاراگراف کامل
- اول یک تیتر جذاب
- آخر لینک منبع

لینک:
{link}
"""

    response = client.chat.completions.create(
        model="gpt-chat-5.3-latest",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


posts = []

with open("news.txt","r",encoding="utf-8") as f:
    data = f.read().split("-----")

for item in data:

    lines = item.strip().split("\n")

    if len(lines) < 3:
        continue

    title = lines[0]
    summary = lines[1]
    link = lines[2]

    post = generate_post(title,summary,link)

    posts.append(post)

with open("rubika_posts.txt","w",encoding="utf-8") as f:

    for p in posts:
        f.write(p+"\n\n")
