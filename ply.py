from playwright.sync_api import sync_playwright
import requests

mp4_url = None

def handle_response(res):
    global mp4_url
    if "full" in res.url and ".mp4" in res.url:
        mp4_url = res.url
        print("✅ Found:", mp4_url)

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,   # 🔥 IMPORTANT (Xvfb will hide it)
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled"
        ]
    )

    context = browser.new_context(
        service_workers="block",
        bypass_csp=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )

    page = context.new_page()

    page.on("response", handle_response)

    page.goto(
        "https://www.xfree.com/video?id=547939&title",
        wait_until="domcontentloaded"
    )

    # accept cookies
    try:
        page.get_by_text("Agree & allow all").click(timeout=5000)
    except:
        pass

    # remove popup
    page.evaluate("document.querySelectorAll('.x-popup').forEach(e => e.remove())")
    page.evaluate("document.body.classList.remove('is-blurred')")

    page.reload()

    page.wait_for_selector("#feed-video-element")

    page.locator("#feed-video-element").click(force=True)

    page.wait_for_timeout(10000)

    browser.close()

# download after browser closes
if mp4_url:
    print("⬇️ Downloading...")
    r = requests.get(mp4_url, stream=True)
    with open("video.mp4", "wb") as f:
        for chunk in r.iter_content(1024 * 1024):
            f.write(chunk)
    print("✅ Download complete")
else:
    print("❌ No mp4 found")
