"""Behave hooks: browser/API lifecycle, per-scenario isolation, failure screenshots.

Config (env vars or `behave -D key=value`):
  BASE_URL  frontend URL          (default http://localhost:5173)
  API_URL   backend URL           (default http://127.0.0.1:8000)
  HEADED    true|false            (default false)  -D headed=true
  SLOWMO    milliseconds          (default 0)      -D slowmo=300
  BROWSER   chromium|msedge|chrome (default: chromium, falling back to msedge, chrome)
"""
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright  # noqa: E402

from pages.booking_page import BookingPage  # noqa: E402

SCREENSHOT_DIR = ROOT / "reports" / "screenshots"


def before_all(context):
    ud = context.config.userdata
    context.base_url = os.getenv("BASE_URL", "http://localhost:5173")
    context.api_url = os.getenv("API_URL", "http://127.0.0.1:8000")
    headed = str(ud.get("headed", os.getenv("HEADED", "false"))).lower() == "true"
    slow_mo = int(ud.get("slowmo", os.getenv("SLOWMO", "0")))

    context.pw = sync_playwright().start()
    context.api = context.pw.request.new_context(base_url=context.api_url)
    try:
        health = context.api.get("/api/health")
        assert health.ok
    except Exception as exc:  # noqa: BLE001
        context.pw.stop()
        raise RuntimeError(
            f"Backend not reachable at {context.api_url}. Start it first (or use run_tests.py)."
        ) from exc
    context.active_bugs = health.json().get("bugs", [])
    print(f"\nBackend bugs active: {context.active_bugs or 'none'}")
    context.browser = _launch_browser(context.pw, ud.get("browser", os.getenv("BROWSER", "")), headed, slow_mo)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def _launch_browser(pw, preferred, headed, slow_mo):
    """Bundled Chromium first; fall back to installed Edge / Chrome if it is not available."""
    candidates = [preferred] if preferred else ["chromium", "msedge", "chrome"]
    errors = []
    for name in candidates:
        try:
            kwargs = {} if name == "chromium" else {"channel": name}
            browser = pw.chromium.launch(headless=not headed, slow_mo=slow_mo, **kwargs)
            print(f"Browser: {name}")
            return browser
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {str(exc).splitlines()[0]}")
    raise RuntimeError("No browser could be launched:\n  " + "\n  ".join(errors))


def before_scenario(context, scenario):
    context.api.post("/api/test/reset")
    context.browser_context = context.browser.new_context(viewport={"width": 1280, "height": 900})
    context.page = context.browser_context.new_page()
    context.page.set_default_timeout(8000)
    context.booking_page = BookingPage(context.page, context.base_url)
    context.booking = {}   # doctor_name, doctor_id, date, time, ...
    context.responses = []  # API responses collected by @api steps


def after_step(context, step):
    if step.status == "failed" and hasattr(context, "page"):
        stamp = datetime.now().strftime("%H%M%S")
        safe = "".join(c if c.isalnum() else "_" for c in context.scenario.name)[:60]
        context.page.screenshot(path=str(SCREENSHOT_DIR / f"{safe}_{stamp}.png"), full_page=True)


def after_scenario(context, scenario):
    context.browser_context.close()


def after_all(context):
    context.browser.close()
    context.api.dispose()
    context.pw.stop()
