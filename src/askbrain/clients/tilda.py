from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from askbrain.clients.base import FeedClient
from askbrain.config import Settings, get_settings
from askbrain.models.feed import FeedPost, FeedResponse, FeedSliceParams, FeedPostStats


class TildaFeedClient(FeedClient):
    def __init__(self, settings: Settings | None = None, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings or get_settings()
        self._client = client or httpx.AsyncClient(timeout=httpx.Timeout(10, connect=5))

    async def __aenter__(self) -> "TildaFeedClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._client.__aexit__(exc_type, exc, tb)

    async def fetch_all_posts(self, feed_uid: str) -> list[FeedPost]:
        posts: list[FeedPost] = []
        params = FeedSliceParams(size=self.settings.tilda_default_size)
        async for response in self._iterate_feed(feed_uid, params):
            posts.extend(response.posts)
        return posts

    async def _iterate_feed(self, feed_uid: str, params: FeedSliceParams) -> AsyncIterator[FeedResponse]:
        next_params: FeedSliceParams | None = params
        while next_params is not None:
            response = await self._fetch_slice(feed_uid, next_params)
            yield response
            next_params = next_params.next_params(response.nextslice)

    async def _fetch_slice(self, feed_uid: str, params: FeedSliceParams) -> FeedResponse:
        url = self._build_url(feed_uid)
        query = {
            "feeduid": feed_uid,
            "size": params.size,
            "slice": params.slice,
            "sort[date]": params.sort_date,
            "filters[date]": "",
            "getparts": "true",
        }

        retrying = self._retry_context()
        async for attempt in retrying:
            with attempt:
                response = await self._client.get(url, params=query, headers=self._headers)
                response.raise_for_status()
                payload = response.json()
                return self._parse_feed(payload)
        raise RuntimeError("Не удалось получить ответ от Tilda API")

    def _retry_context(self) -> AsyncRetrying:
        return AsyncRetrying(
            retry=retry_if_exception_type(httpx.HTTPError),
            stop=stop_after_attempt(5),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            reraise=True,
        )

    @property
    def _headers(self) -> dict[str, str]:
        return {"Origin": str(self.settings.origin_host), "Referer": str(self.settings.origin_host)}

    def _build_url(self, feed_uid: str) -> str:
        return "https://feeds.tildaapi.com/api/getfeed/"

    def _parse_feed(self, payload: dict[str, Any]) -> FeedResponse:
        posts = [self._parse_post(raw) for raw in payload.get("posts", [])]
        return FeedResponse(
            feeduid=payload.get("feeduid", ""),
            posts=posts,
            slice=payload.get("slice", 1),
            total=payload.get("total", len(posts)),
            nextslice=payload.get("nextslice"),
        )

    def _parse_post(self, raw: dict[str, Any]) -> FeedPost:
        parts = [part.get("parttitle", "") for part in raw.get("postparts", []) if part.get("parttitle")]
        stats = raw.get("stats", {})
        return FeedPost(
            uid=raw.get("uid", ""),
            title=raw.get("title", ""),
            url=raw.get("url", ""),
            published=raw.get("published"),
            stats=FeedPostStats(views=stats.get("views", 0), likes=stats.get("likes", 0)),
            parts=parts,
            image=raw.get("image"),
            descr=raw.get("descr"),
            text=raw.get("text"),
        )

