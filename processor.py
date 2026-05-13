from openai import OpenAI
import urllib3

urllib3.disable_warnings()

client = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key=api_key,
    default_headers={"X-Ignore-SSL": "1"}
)
