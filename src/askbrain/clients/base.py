from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from askbrain.models.feed import FeedPost


class FeedClient(ABC):
    @abstractmethod
    async def fetch_all_posts(self, feed_uid: str) -> list[FeedPost]:
        ...

    async def fetch_multiple(self, feed_uids: Iterable[str]) -> dict[str, list[FeedPost]]:
        results: dict[str, list[FeedPost]] = {}
        for feed_uid in feed_uids:
            results[feed_uid] = await self.fetch_all_posts(feed_uid)
        return results

