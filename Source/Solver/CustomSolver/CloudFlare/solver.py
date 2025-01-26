from __future__ import annotations

import argparse
import json
import logging
import re
import urllib.parse as urlparse
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional

from patchright.async_api import Cookie  # Change to async imports
from patchright.async_api import Error as PlaywrightError
from patchright.async_api import Frame, async_playwright  # Use async_playwright

class ChallengePlatform(Enum):
    JAVASCRIPT = "non-interactive"
    MANAGED = "managed"
    INTERACTIVE = "interactive"

class CloudflareSolver:
    def __init__(
        self,
        *,
        user_agent: str,
        timeout: float,
        http2: bool,
        http3: bool,
        headless: bool,
        proxy: Optional[str],
    ) -> None:
        self._playwright = None
        self.browser = None
        self.page = None
        self.timeout = timeout
        self.user_agent = user_agent
        self.proxy = proxy
        self.http2 = http2
        self.http3 = http3
        self.headless = headless

    async def setup_browser(self):

        self._playwright = await async_playwright().start()
        args = []

        if not self.http2:
            args.append("--disable-http2")

        if not self.http3:
            args.append("--disable-quic")

        if self.proxy:
            self.proxy = self._parse_proxy(self.proxy)

        self.browser = await self._playwright.chromium.launch(
            args=args, headless=self.headless, proxy=self.proxy
        )

        context = await self.browser.new_context(user_agent=self.user_agent)
        context.set_default_timeout(self.timeout * 1000)
        self.page = await context.new_page()

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    @staticmethod
    def _parse_proxy(proxy: str) -> Dict[str, str]:
        parsed_proxy = urlparse.urlparse(proxy)
        server = f"{parsed_proxy.scheme}://{parsed_proxy.hostname}"
        if parsed_proxy.port is not None:
            server += f":{parsed_proxy.port}"

        proxy_params = {"server": server}

        if parsed_proxy.username is not None and parsed_proxy.password is not None:
            proxy_params.update(
                {"username": parsed_proxy.username, "password": parsed_proxy.password}
            )

        return proxy_params

    def _get_turnstile_frame(self) -> Optional[Frame]:
        return self.page.frame(
            url=re.compile(
                "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/[bg]/turnstile"
            ),
        )

    @property
    async def cookies(self) -> List[Cookie]:
        return await self.page.context.cookies()

    @staticmethod
    def extract_clearance_cookie(cookies: Iterable[Cookie]) -> Optional[Cookie]:
        for cookie in cookies:
            if cookie["name"] == "cf_clearance":
                return cookie
        return None

    async def detect_challenge(self) -> Optional[ChallengePlatform]:
        html = await self.page.content()
        for platform in ChallengePlatform:
            if f"cType: '{platform.value}'" in html:
                return platform
        return None

    async def solve_challenge(self) -> None:
     verify_button_pattern = re.compile(
        "Verify (I am|you are) (not a bot|(a )?human)"
    )
    
     verify_button = self.page.locator("button", has_text=verify_button_pattern)
     challenge_spinner = self.page.locator("#challenge-spinner")
     challenge_stage = self.page.locator("#challenge-stage")
     start_timestamp = datetime.now()

     while (
        self.extract_clearance_cookie(await self.cookies) is None
        and await self.detect_challenge() is not None
        and (datetime.now() - start_timestamp).seconds < self.timeout
    ):
        if await challenge_spinner.is_visible():
            await challenge_spinner.wait_for(state="hidden")

        turnstile_frame = self._get_turnstile_frame()

        if await verify_button.is_visible():
            await verify_button.click()
            await challenge_stage.wait_for(state="hidden")
        elif turnstile_frame is not None:
            await self.page.mouse.click(210, 290)
            await challenge_stage.wait_for(state="hidden")

        await self.page.wait_for_timeout(250)







