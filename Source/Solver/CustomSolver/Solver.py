import asyncio
from collections import deque
from colorama import *


class PagePool:
    def __init__(self, context, debug: bool = False, log=None):
        self.context = context
        self.min_size = 1
        self.max_size = 10
        self.available_pages: deque = deque()
        self.in_use_pages: set = set()
        self._lock = asyncio.Lock()
        self.debug = debug
        self.log = log

    async def initialize(self):
        for _ in range(self.min_size):
            page = await self.context.new_page()
            self.available_pages.append(page)

    async def get_page(self):
        async with self._lock:
            if (not self.available_pages and
                    len(self.in_use_pages) < self.max_size):
                page = await self.context.new_page()
    
            else:
                while not self.available_pages:
                    await asyncio.sleep(0.1)
                page = self.available_pages.popleft()

            self.in_use_pages.add(page)
            return page

    async def return_page(self, page):
        async with self._lock:
            self.in_use_pages.remove(page)
            total_pages = len(self.available_pages) + len(self.in_use_pages) + 1
            if total_pages > self.min_size and len(self.available_pages) >= 2:
                await page.close()
            else:
                self.available_pages.append(page)