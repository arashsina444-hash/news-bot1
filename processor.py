import os
import requests
import time
import traceback
from datetime import datetime

NEWS_FILE = "news.txt"
OUTPUT_FILE = "rubika_posts.txt"
LOG_FILE = "run_log.txt"

API_KEY = os.getenv("GAPGPT_API_KEY")
MODEL = "gpt-5.1-chat-latest"

API_URL = "https://api.gapgpt.app/v1/chat/completions"

TIMEOUT = 40
RETRIES = 6


def log(text):
    t = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{t}] {text}"
    print(line)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def internet_test():

    try:
        requests.get("https://api.gapgpt.app", timeout=10)
        log("GapGPT reachable")
        return True
    except:
        log("GapGPT not reachable")
        return False


def read_news():

    if not os.path.exists(NEWS_FILE):
        raise Exception("news.txt not found")

    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(news):

    return f"""
از خبر زیر یک پست کوتاه و جذاب برای روبیکا بنویس.

قوانین:
تیتر کوتاه
۲ تا ۳ خط توضیح
لحن خبری و ساده

خبر:
{news}
"""


def call_ai(prompt):

    session = requests.Session()

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    for attempt in range(RETRIES):

        try:

            log(f"AI request attempt {attempt+1}")

            r = session.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=TIMEOUT
            )

            log(f"status {r.status_code}")

            if r.status_code == 200:

                data = r.json()

                return data["choices"][0]["message"]["content"]

        except Exception as e:

            log(str(e))

        time.sleep(2 ** attempt)

    raise Exception("AI failed after retries")


def main():

    log("===== start =====")

    try:

        news = read_news()

        if not internet_test():

            raise Exception("API unreachable")

        prompt = build_prompt(news)

        try:

            result = call_ai(prompt)

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(result)

            log("AI text generated")

        except Exception as ai_error:

            log("AI error")

            err = "".join(traceback.format_exception(
                type(ai_error),
                ai_error,
                ai_error.__traceback__
            ))

            log(err)

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("❌ دریافت پاسخ از GapGPT ممکن نشد")

    except Exception as e:

        err = "".join(traceback.format_exception(
            type(e),
            e,
            e.__traceback__
        ))

        log(err)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("❌ خطا در پردازش خبر")

    log("===== end =====")


if __name__ == "__main__":
    main()
