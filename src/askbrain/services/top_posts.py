from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from askbrain.clients.base import FeedClient
from askbrain.models.feed import FeedPost

logger = logging.getLogger(__name__)


@dataclass
class TopPostsResult:
    fetched_at: datetime
    posts: list[FeedPost]
    source_feeds: tuple[str, ...]
    total_posts: int


class TopPostsService:
    def __init__(self, client: FeedClient, limit: int = 3, concurrency: int = 2) -> None:
        self.client = client
        self.limit = limit
        self.concurrency = max(1, concurrency)

    async def fetch_top_posts(self, feed_uids: Iterable[str]) -> TopPostsResult:
        feed_list = tuple(feed_uids)
        posts = await self._collect_posts(feed_list)
        unique_posts = {post.uid: post for post in posts}.values()
        top_posts = sorted(unique_posts, key=lambda post: post.stats.views, reverse=True)[: self.limit]
        fetched_at = datetime.now(tz=timezone.utc)
        return TopPostsResult(
            fetched_at=fetched_at,
            posts=top_posts,
            source_feeds=feed_list,
            total_posts=len(posts),
        )

    async def _collect_posts(self, feed_uids: tuple[str, ...]) -> list[FeedPost]:
        semaphore = asyncio.Semaphore(self.concurrency)
        tasks = [asyncio.create_task(self._fetch_feed(feed_uid, semaphore)) for feed_uid in feed_uids]

        posts: list[FeedPost] = []
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                posts.extend(result)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Не удалось получить посты", exc_info=exc)
        return posts

    async def _fetch_feed(self, feed_uid: str, semaphore: asyncio.Semaphore) -> list[FeedPost]:
        async with semaphore:
            logger.info("Загружаем посты из фида %s", feed_uid)
            posts = await self.client.fetch_all_posts(feed_uid)
            logger.info("Получено %s постов из фида %s", len(posts), feed_uid)
            return posts

