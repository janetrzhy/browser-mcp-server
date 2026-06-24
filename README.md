# Browser MCP Server — 眼睛

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-7C3AED.svg)](https://modelcontextprotocol.io/)
[![Playwright](https://img.shields.io/badge/Playwright-Chromium-45ba4b.svg)](https://playwright.dev/)

**An MCP server that gives AI assistants eyes on the web.** This project implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) to bridge AI language models (like Claude, GPT, etc.) with a headless Chromium browser, enabling autonomous web interaction — navigating, clicking, typing, scrolling, and extracting content.

> "眼睛" (Yǎnjīng) means "eyes" in Chinese — because that's exactly what this gives an AI.

---

## Features

| Tool | Description |
|---|---|
| `navigate(url)` | Open a URL and return the page title |
| `screenshot()` | Capture a full-page screenshot (base64 PNG) |
| `click(x, y)` | Click at specific pixel coordinates |
| `type_text(text)` | Type text with realistic keystroke timing |
| `press_key(key)` | Press keyboard keys (Enter, Tab, Escape, etc.) |
| `scroll(dir, px)` | Scroll up or down by a given amount |
| `extract_text()` | Extract all visible text from the page |
| `get_links()` | List all links with their text labels |

All tools share a single persistent browser session — state (cookies, local storage, navigation history) is maintained between calls.

---

## Architecture

```
┌────────────┐     MCP Protocol      ┌──────────────┐     Playwright     ┌──────────┐
│   AI       │ ◄──────────────────►  │   MCP Server  │ ◄──────────────►  │ Chromium │
│  Assistant  │     streamable-http   │  (server.py)  │    async API      │ (Headless)│
│ (Claude,etc)│                      │  :3001        │                   │          │
└────────────┘                       └──────┬───────┘                   └──────────┘
                                            │
                                    ┌───────┴────────┐
                                    │ Cloudflare Tunnel│  (optional, for remote access)
                                    │ trycloudflare.com│
                                    └────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- [Playwright browsers](https://playwright.dev/docs/browsers): `playwright install chromium`

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/browser-mcp-server.git
cd browser-mcp-server

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright Chromium
playwright install chromium
```

### Run Locally

```bash
python server.py
```

The server starts on `http://0.0.0.0:3001` using the `streamable-http` transport. Configure your MCP client (Claude Desktop, VS Code extension, etc.) to connect to this endpoint with the path `/sse`.

Example MCP client configuration:

```json
{
  "mcpServers": {
    "眼睛": {
      "url": "http://localhost:3001/sse"
    }
  }
}
```

---

## Remote Deployment (GitHub Actions + Cloudflare Tunnel)

This project includes a GitHub Actions workflow that runs the server for up to **6 hours** and exposes it via a Cloudflare Tunnel — no public IP or VPS required.

### How It Works

1. **Trigger** the workflow manually from the GitHub Actions tab
2. The runner installs Python + Playwright + Chromium + `cloudflared`
3. The MCP server starts, and a Cloudflare Tunnel creates a public `*.trycloudflare.com` URL
4. The tunnel URL is printed in the workflow logs — append `/sse` and use it in your MCP client
5. The runner stays alive for up to 6 hours, then shuts down automatically

### Usage

```bash
gh workflow run browser.yml
# Grab the tunnel URL from the logs
# Configure your MCP client: https://xxxx.trycloudflare.com/sse
```

---

## API Reference

### `navigate(url: str) -> str`
Opens a URL in the browser. Waits for `DOMContentLoaded` (up to 15s timeout). Returns the page title and current URL.

### `screenshot() -> str`
Returns a data URI string: `data:image/png;base64,...` suitable for embedding directly in Markdown or HTML.

### `click(x: int, y: int) -> str`
Clicks at pixel coordinates `(x, y)` relative to the viewport. Waits 1 second after the click for page reactions.

### `type_text(text: str) -> str`
Types the given text character by character with a **50ms delay** between keystrokes, mimicking human typing speed.

### `press_key(key: str) -> str`
Presses a single keyboard key. Accepts standard key names: `Enter`, `Tab`, `Escape`, `ArrowUp`, `ArrowDown`, `Backspace`, etc.

### `scroll(direction: str = "down", amount: int = 500) -> str`
Scrolls the page by `amount` pixels in the given `direction` (`"up"` or `"down"`).

### `extract_text() -> str`
Extracts all visible text from `document.body`. Capped at **5,000 characters** to keep responses efficient.

### `get_links() -> str`
Extracts up to **50** links with their visible text labels, formatted as `[label] -> url`.

---

## Use Cases

- **AI-powered web testing** — automate form filling, button clicking, and content verification
- **Research & data collection** — navigate to sources, extract content, take screenshots
- **Visual monitoring** — periodically capture screenshots of dashboards or live pages
- **Prototype automation** — quickly script browser interactions using natural language through an AI assistant
- **Demo & presentation** — let an AI walk through your web app live

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Protocol** | [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) |
| **Python Framework** | [FastMCP](https://github.com/jlowin/fastmcp) |
| **Browser Automation** | [Playwright](https://playwright.dev/) (async API) |
| **Tunnel** | [Cloudflare Tunnel (cloudflared)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) |
| **CI/CD** | [GitHub Actions](https://github.com/features/actions) |

---

## Project Structure

```
browser-mcp-server/
├── server.py                    # MCP server entry point
├── requirements.txt             # Python dependencies
├── .github/workflows/browser.yml  # GitHub Actions deployment workflow
├── .gitignore
└── README.md
```

---

## Contributing

Contributions are welcome! If you have ideas for new tools, improvements, or bug fixes:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-idea`)
3. Commit your changes (`git commit -m 'Add amazing idea'`)
4. Push to the branch (`git push origin feature/amazing-idea`)
5. Open a Pull Request

---

## License

[MIT](LICENSE) © 2025

---

## Why This Exists

Large Language Models are incredibly capable at understanding and generating text, but they are **blind to the live web**. They don't know what a page looks like right now, whether a button is clickable, or what a search actually returns. This server closes that gap — it's a minimal, focused bridge that lets AI **see and interact** with the web in real time.

Built for the [Model Context Protocol](https://modelcontextprotocol.io/) ecosystem.
