"""
Browser MCP Server — "S的眼睛" (S's Eyes)

A Model Context Protocol (MCP) server that bridges AI assistants with a headless
Chromium browser, enabling autonomous web browsing, screenshot capture,
form filling, and content extraction.
"""

import asyncio
import base64
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright, Browser, Page

# Global browser state — lazily initialized on first tool call
browser: Browser | None = None
page: Page | None = None
playwright_instance = None


async def get_page() -> Page:
    """Get or create the shared browser page instance."""
    global browser, page, playwright_instance

    if browser is None:
        playwright_instance = await async_playwright().start()
        browser = await playwright_instance.chromium.launch(
            headless=True,  # No display available in CI/GitHub Actions
            args=["--window-size=1280,800", "--no-sandbox"],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800}, locale="zh-CN"
        )
        page = await context.new_page()
    return page


mcp = FastMCP("S的眼睛", host="0.0.0.0", port=3001)


@mcp.tool()
async def navigate(url: str) -> str:
    """Navigate to a URL and return the page title and current URL."""
    p = await get_page()
    try:
        await p.goto(url, wait_until="domcontentloaded", timeout=15000)
        return f"Navigated: {p.title} ({p.url})"
    except Exception as e:
        return f"Navigation failed: {str(e)}"


@mcp.tool()
async def screenshot() -> str:
    """Take a screenshot of the current page and return it as a base64 PNG."""
    p = await get_page()
    img_bytes = await p.screenshot(type="png")
    img_b64 = base64.b64encode(img_bytes).decode()
    return f"data:image/png;base64,{img_b64}"


@mcp.tool()
async def click(x: int, y: int) -> str:
    """Click at the specified pixel coordinates (x, y) on the page."""
    p = await get_page()
    await p.mouse.click(x, y)
    await asyncio.sleep(1)
    return f"Clicked at ({x}, {y})"


@mcp.tool()
async def type_text(text: str) -> str:
    """Type text into the currently focused element with a 50ms keystroke delay."""
    p = await get_page()
    await p.keyboard.type(text, delay=50)
    return f"Typed: {text}"


@mcp.tool()
async def press_key(key: str) -> str:
    """Press a keyboard key (e.g., Enter, Tab, Escape, ArrowDown)."""
    p = await get_page()
    await p.keyboard.press(key)
    return f"Pressed: {key}"


@mcp.tool()
async def scroll(direction: str = "down", amount: int = 500) -> str:
    """Scroll the page. Direction: 'up' or 'down'; amount is in pixels."""
    p = await get_page()
    delta = amount if direction == "down" else -amount
    await p.mouse.wheel(0, delta)
    await asyncio.sleep(0.5)
    return f"Scrolled {direction} by {amount}px"


@mcp.tool()
async def extract_text() -> str:
    """Extract all visible text from the current page (capped at 5000 chars)."""
    p = await get_page()
    text = await p.inner_text("body")
    if len(text) > 5000:
        text = text[:5000] + "\n...(truncated at 5000 characters)"
    return text


@mcp.tool()
async def get_links() -> str:
    """Extract up to 50 links from the current page with their text labels."""
    p = await get_page()
    links = await p.eval_on_selector_all(
        "a[href]",
        "els => els.map(e => ({text: e.innerText.trim(), href: e.href})).filter(e => e.text).slice(0, 50)",
    )
    result = "\n".join([f"[{l['text']}] -> {l['href']}" for l in links])
    return result or "No links found"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
