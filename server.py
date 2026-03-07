import asyncio
import base64
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright, Browser, Page

browser: Browser | None = None
page: Page | None = None
playwright_instance = None

async def get_page() -> Page:
    global browser, page, playwright_instance
    if browser is None:
        playwright_instance = await async_playwright().start()
        browser = await playwright_instance.chromium.launch(
            headless=True,  # GitHub Actions没有显示器
            args=['--window-size=1280,800', '--no-sandbox']
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            locale='zh-CN'
        )
        page = await context.new_page()
    return page

mcp = FastMCP("S的眼睛", host="0.0.0.0", port=3001)

@mcp.tool()
async def navigate(url: str) -> str:
    """打开指定网页URL"""
    p = await get_page()
    try:
        await p.goto(url, wait_until="domcontentloaded", timeout=15000)
        return f"已打开: {p.title} ({p.url})"
    except Exception as e:
        return f"打开失败: {str(e)}"

@mcp.tool()
async def screenshot() -> str:
    """对当前页面截图，返回base64图片"""
    p = await get_page()
    img_bytes = await p.screenshot(type="png")
    img_b64 = base64.b64encode(img_bytes).decode()
    return f"data:image/png;base64,{img_b64}"

@mcp.tool()
async def click(x: int, y: int) -> str:
    """点击页面上指定坐标(x,y)"""
    p = await get_page()
    await p.mouse.click(x, y)
    await asyncio.sleep(1)
    return f"已点击坐标 ({x}, {y})"

@mcp.tool()
async def type_text(text: str) -> str:
    """在当前焦点位置输入文字"""
    p = await get_page()
    await p.keyboard.type(text, delay=50)
    return f"已输入: {text}"

@mcp.tool()
async def press_key(key: str) -> str:
    """按下键盘按键，如Enter, Tab, Escape等"""
    p = await get_page()
    await p.keyboard.press(key)
    return f"已按下: {key}"

@mcp.tool()
async def scroll(direction: str = "down", amount: int = 500) -> str:
    """滚动页面。direction: up/down, amount: 像素数"""
    p = await get_page()
    delta = amount if direction == "down" else -amount
    await p.mouse.wheel(0, delta)
    await asyncio.sleep(0.5)
    return f"已向{direction}滚动{amount}像素"

@mcp.tool()
async def extract_text() -> str:
    """提取当前页面的文字内容"""
    p = await get_page()
    text = await p.inner_text("body")
    if len(text) > 5000:
        text = text[:5000] + "\n...(内容过长已截断)"
    return text

@mcp.tool()
async def get_links() -> str:
    """获取当前页面所有链接"""
    p = await get_page()
    links = await p.eval_on_selector_all(
        "a[href]",
        "els => els.map(e => ({text: e.innerText.trim(), href: e.href})).filter(e => e.text).slice(0, 50)"
    )
    result = "\n".join([f"[{l['text']}] -> {l['href']}" for l in links])
    return result or "未找到链接"

if __name__ == "__main__":
    mcp.run(transport="sse")