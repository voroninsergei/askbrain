from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class FeedPostStats(BaseModel):
    views: int = 0
    likes: int = 0


class FeedPost(BaseModel):
    uid: str
    title: str
    url: str
    published: datetime
    stats: FeedPostStats = Field(default_factory=FeedPostStats)
    parts: list[str] = Field(default_factory=list)
    image: Optional[str] = None
    descr: Optional[str] = None
    text: Optional[str] = None


class FeedResponse(BaseModel):
    feeduid: str
    posts: list[FeedPost]
    slice: int
    total: int
    nextslice: Optional[int] = None


class FeedSliceParams(BaseModel):
    size: int
    slice: int = 1
    sort_date: Literal["desc", "asc"] = "desc"

    def next_params(self, next_slice: Optional[int]) -> Optional["FeedSliceParams"]:
        if next_slice is None:
            return None
        return FeedSliceParams(size=self.size, slice=next_slice, sort_date=self.sort_date)

