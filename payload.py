from playwright.sync_api import sync_playwright
import json
from time import sleep

TARGET_URL_PART = "searchJobsV3"


def parse_cookie_string(cookie_string):
    cookies = []
    for item in cookie_string.split("; "):
        if "=" in item:
            name, value = item.split("=", 1)
            cookies.append({
                "name": name,
                "value": value,
                "domain": ".glints.com",
                "path": "/",
                "secure": True
            })
    return cookies


def get_payload(raw_cookies,url):
    intercepted_payload = None  # 🎯 penampung hasil

    def intercept_request(request):
        nonlocal intercepted_payload

        if TARGET_URL_PART in request.url and request.method == "POST":
            print("\n🔥 GraphQL request terdeteksi")

            post_data = request.post_data
            if post_data:
                try:
                    intercepted_payload = json.loads(post_data)
                    print("✅ Payload JSON berhasil di-parse")
                except:
                    intercepted_payload = {}  # kalau gagal parse
                    print("⚠️ Payload bukan JSON valid → diset {}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.add_cookies(parse_cookie_string(raw_cookies))

        page = context.new_page()
        page.on("request", intercept_request)

        page.goto(
            url,
            wait_until="domcontentloaded"
        )
        max_wait = 10#second
        for _ in range(max_wait):
            if intercepted_payload:break
            sleep(1) 
        browser.close()

    return intercepted_payload



