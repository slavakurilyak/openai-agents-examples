import asyncio
import base64
import logging
from typing import List, Literal
import os
from playwright.async_api import Browser, Page, Playwright, async_playwright

from agents import (
    Agent,
    AsyncComputer,
    Button,
    ComputerTool,
    Environment,
    ModelSettings,
    Runner,
    trace,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalPCComputer(AsyncComputer):
    """A computer implementation using Playwright to automate desktop/browser tasks."""

    def __init__(self):
        self._playwright = None
        self._browser = None
        self._page = None

    async def _get_browser_and_page(self) -> tuple[Browser, Page]:
        width, height = self.dimensions
        launch_args = [f"--window-size={width},{height}"]
        browser = await self.playwright.chromium.launch(headless=False, args=launch_args)
        page = await browser.new_page()
        await page.set_viewport_size({"width": width, "height": height})
        # Start at GitHub's OpenAI Agents repo
        await page.goto("https://github.com/openai/openai-agents-python")
        return browser, page

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser, self._page = await self._get_browser_and_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    @property
    def playwright(self) -> Playwright:
        assert self._playwright is not None
        return self._playwright

    @property
    def browser(self) -> Browser:
        assert self._browser is not None
        return self._browser

    @property
    def page(self) -> Page:
        assert self._page is not None
        return self._page

    @property
    def environment(self) -> Environment:
        return "browser"

    @property
    def dimensions(self) -> tuple[int, int]:
        return (1280, 800)

    async def screenshot(self) -> str:
        """Capture the viewport."""
        png_bytes = await self.page.screenshot(full_page=False)
        return base64.b64encode(png_bytes).decode("utf-8")

    async def click(self, x: int, y: int, button: Button = "left") -> None:
        playwright_button: Literal["left", "middle", "right"] = "left"
        if button in ("left", "right", "middle"):
            playwright_button = button  # type: ignore
        await self.page.mouse.click(x, y, button=playwright_button)

    async def double_click(self, x: int, y: int) -> None:
        await self.page.mouse.dblclick(x, y)

    async def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        await self.page.mouse.move(x, y)
        await self.page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")

    async def type(self, text: str) -> None:
        await self.page.keyboard.type(text)

    async def wait(self) -> None:
        await asyncio.sleep(1)

    async def move(self, x: int, y: int) -> None:
        await self.page.mouse.move(x, y)

    async def keypress(self, keys: List[str]) -> None:
        for key in keys:
            # Map keys if needed for playwright
            key_map = {
                "alt": "Alt",
                "ctrl": "Control",
                "cmd": "Meta",
                "enter": "Enter",
                "esc": "Escape",
                "tab": "Tab",
                "space": " ",
            }
            mapped_key = key_map.get(key.lower(), key)
            await self.page.keyboard.press(mapped_key)

    async def drag(self, path: List[tuple[int, int]]) -> None:
        if not path:
            return
        await self.page.mouse.move(path[0][0], path[0][1])
        await self.page.mouse.down()
        for px, py in path[1:]:
            await self.page.mouse.move(px, py)
        await self.page.mouse.up()


async def main():
    """Run an agent that sets up an agent development environment."""
    
    async with LocalPCComputer() as computer:
        with trace("Agent Dev Setup Workflow"):
            agent = Agent(
                name="Agent Dev Setup Assistant",
                instructions="""You are a specialized agent that helps developers set up an environment for building AI agents.
                
                Your capabilities include:
                1. Browse GitHub to find agent frameworks and repositories
                2. Clone repositories and set up development environments
                3. Navigate documentation to find key examples and getting started guides
                4. Help create initial project structure for a new agent
                
                For this session, focus on:
                1. Navigating the OpenAI Agents SDK repository
                2. Finding key examples in the repository
                3. Identifying the main components needed to build an agent
                
                Walk through the repository and provide guidance on what parts would be most useful for a
                developer just getting started with building agents.
                """,
                tools=[ComputerTool(computer)],
                model="computer-use-preview",
                model_settings=ModelSettings(truncation="auto"),
            )
            
            result = await Runner.run(
                agent,
                """I'm a developer looking to create my first agent using the OpenAI Agents SDK.
                Please help me understand the repository structure and identify the key examples
                I should look at to get started. Specifically, what are the core components for
                building a multi-agent system? Take screenshots as you navigate to help me visualize
                the repository structure."""
            )
            
            print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())