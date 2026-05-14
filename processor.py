import os
import json
import time
import traceback
from datetime import datetime

import requests

# -----------------------------
# تنظیمات اصلی
# -----------------------------
NEWS_FILE = "news.txt"
OUTPUT_FILE = "rubika_posts.txt"
LOG_FILE = "run_log.txt"

# مدل و API
MODEL_NAME = "gpt-5.3-chat-latest"
API_KEY_ENV = "GAPGPT_API_KEY"

# دو اندپوینت برای Failover
ENDPOINTS = [
    "https://api.gapgpt.app/v1/chat/completions",
    "https://api.gapgpt.com/v1/chat/completions",
]

# تعداد تلاش برای هر اندپوینت
MAX_RETRIES_PER_ENDPOINT = 3

# Timeout برای هر درخواست
REQUEST_TIMEOUT = 15  # ثانیه

# User-Agent برای کاهش احتمال بلاک Cloudflare
DEFAULT_HEADERS = {
    "User-Agent": "GapGPT-NewsBot/1.0 (+https://github.com)",
}


def log(message: str):
    """نوشتن پیام در کنسول و فایل لاگ."""
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {message}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # اگر نوشتن لاگ هم خطا داد، نباید برنامه بترکد
        pass


def read_news() -> str:
    """خواندن محتویات news.txt"""
    if not os.path.exists(NEWS_FILE):
        raise FileNotFoundError(f"{NEWS_FILE} not found")

    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        raise ValueError(f"{NEWS_FILE} is empty")

    return content


def build_prompt(news_content: str) -> str:
    """ساخت پرامپت برای مدل."""
    prompt = f"""
تو یک ربات نویسنده‌ی پست برای روبیکا هستی.
بر اساس متن خبر زیر، یک پست کوتاه، جذاب و قابل فهم به زبان فارسی تولید کن.
اجزاء پست:
- یک تیتر جذاب
- خلاصه‌ی بسیار کوتاه (۲–۳ خط)
- در صورت نیاز، یک دعوت به ادامه‌ی خبر (مثلاً: برای دیدن جزئیات بیشتر…)

قوانین:
- از شکلک‌های زیاد استفاده نکن، نهایتاً ۱–۲ تا در متن باشد.
- از نوشتن لینک خودداری کن.
- لحن: صمیمی اما محترمانه.
- طول کل متن حداکثر حدود ۸۰۰ کاراکتر باشد.

متن خبر:
----------------
{news_content}
----------------

خروجی را فقط به صورت یک متن آماده برای ارسال در روبیکا برگردان.
"""
    return prompt.strip()


def call_gapgpt(api_key: str, endpoint: str, prompt: str) -> str:
    """یک بار تماس با GapGPT."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        **DEFAULT_HEADERS,
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 600,
    }

    resp = requests.post(
        endpoint,
        headers=headers,
        data=json.dumps(payload),
        timeout=REQUEST_TIMEOUT,
    )

    # اگر کد وضعیت غیر از 2xx بود، خطا بدهیم
    if not 200 <= resp.status_code < 300:
        raise RuntimeError(
            f"Non-2xx status code from {endpoint}: {resp.status_code} - {resp.text[:200]}"
        )

    data = resp.json()
    # ساختار استاندارد OpenAI-like:
    # { choices: [ { message: { content: "..."} } ] }
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise ValueError(f"Unexpected response JSON structure: {data}")

    return content.strip()


def generate_posts_with_failover(news_content: str) -> str:
    """تلاش برای گرفتن پاسخ از GapGPT با Failover و Retry."""
    api_key = os.getenv(API_KEY_ENV)
    if not api_key:
        raise EnvironmentError(f"{API_KEY_ENV} is not set")

    prompt = build_prompt(news_content)

    last_error = None

    for endpoint in ENDPOINTS:
        log(f"Trying endpoint: {endpoint}")

        for attempt in range(1, MAX_RETRIES_PER_ENDPOINT + 1):
            try:
                log(
                    f"Request attempt {attempt}/{MAX_RETRIES_PER_ENDPOINT} "
                    f"for endpoint {endpoint}"
                )
                response_text = call_gapgpt(api_key, endpoint, prompt)
                log(f"Success from endpoint {endpoint} on attempt {attempt}")
                return response_text

            except Exception as e:
                last_error = e
                log(
                    f"Error on endpoint {endpoint} attempt {attempt}: "
                    f"{repr(e)}"
                )
                # Backoff ساده: 1، 2، 4 ثانیه ...
                sleep_sec = min(8, 2 ** (attempt - 1))
                log(f"Sleeping {sleep_sec} seconds before retry...")
                time.sleep(sleep_sec)

        log(f"Endpoint {endpoint} failed after {MAX_RETRIES_PER_ENDPOINT} attempts.")

    # اگر به اینجا رسیدیم یعنی هر دو endpoint fail شده‌اند
    raise RuntimeError(
        f"All endpoints failed. Last error: {repr(last_error)}"
    )


def write_output(text: str):
    """نوشتن خروجی در rubika_posts.txt"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")


def main():
    log("===== Processor started =====")

    try:
        news_content = read_news()
        log("news.txt loaded successfully.")

        try:
            ai_response = generate_posts_with_failover(news_content)
            write_output(ai_response)
            log("AI response written to rubika_posts.txt successfully.")

        except Exception as api_error:
            # اگر تماس با API شکست خورد، Fallback
            log("Failed to get valid response from GapGPT.")
            log("API error detail:\n" + "".join(traceback.format_exception(api_error)))

            fallback_text = (
                "❌ پاسخ معتبر از GapGPT دریافت نشد. "
                "ممکن است مشکل موقت در اتصال سرور یا محدودیت شبکه GitHub Actions باشد.\n"
                "لطفاً بعداً مجدداً تلاش کنید."
            )
            write_output(fallback_text)
            log("Fallback text written to rubika_posts.txt.")

    except Exception as e:
        # اگر مشکل از خود فایل news.txt یا چیز دیگر باشد، باز هم نباید Workflow بترکد
        log("Fatal error in processor:")
        log("".join(traceback.format_exception(e)))

        fallback_text = (
            "❌ خطا در پردازش خبرها. "
            "فایل news.txt ممکن است خالی یا در دسترس نباشد.\n"
            "لطفاً تنظیمات را بررسی کنید."
        )
        try:
            write_output(fallback_text)
        except Exception:
            # حتی اگر این هم شکست خورد، فقط لاگ می‌کنیم
            log("Failed to write fallback output file.")

    log("===== Processor finished =====")


if __name__ == "__main__":
    main()
