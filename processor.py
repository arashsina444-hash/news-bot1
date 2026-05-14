import requests
import json
import time
import os
from datetime import datetime

API_URLS = [
    "https://api.gapgpt.app/v1/chat/completions",
    "https://api.gapgpt.com/v1/chat/completions"
]

API_KEY = os.getenv("GAPGPT_API_KEY")

OUTPUT_FILE = "rubika_posts.txt"
LOG_FILE = "run_log.txt"


def log(message):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def call_api(payload):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    for url in API_URLS:
        for attempt in range(1, 4):
            try:
                log(f"Trying: {url} | Attempt {attempt}")
                response = requests.post(url, json=payload, headers=headers, timeout=15)

                if response.status_code == 200:
                    log(f"SUCCESS from {url}")
                    return response.text

                log(f"Non-200 Response {response.status_code}: {response.text}")

            except Exception as e:
                log(f"Error: {str(e)}")

            time.sleep(5 * attempt)

    return None


def create_fallback_output():
    fallback_text = "❗ خطا در اتصال به GapGPT — پاسخ دریافت نشد.\n"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(fallback_text)

    log("Fallback output created due to API failure.")


def main():
    log("=== PROCESSOR STARTED ===")

    prompt_text = (
        "یک پست ۵ جمله‌ای جذاب، کوتاه و مناسب روبیکا بنویس."
    )

    payload = {
        "model": "gpt-5.2-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt_text}
        ],
        "max_tokens": 200
    }

    api_result = call_api(payload)

    if api_result is None:
        create_fallback_output()
        return

    try:
        result_json = json.loads(api_result)
        text = result_json["choices"][0]["message"]["content"].strip()

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(text)

        log("Output file written successfully.")

    except Exception as e:
        log(f"JSON Parse Error: {str(e)}")
        create_fallback_output()


if __name__ == "__main__":
    main()
