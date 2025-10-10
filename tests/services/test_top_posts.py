import pytest

from askbrain.models.feed import FeedPost, FeedPostStats
from askbrain.services.top_posts import TopPostsService


class DummyClient:
    def __init__(self, posts_by_feed):
        self.posts_by_feed = posts_by_feed

    async def fetch_all_posts(self, feed_uid):
        return self.posts_by_feed.get(feed_uid, [])


@pytest.mark.asyncio
async def test_top_posts_sorted_and_limited():
    posts_feed1 = [
        FeedPost(uid="a", title="A", url="u1", published="2025-10-09", stats=FeedPostStats(views=5)),
        FeedPost(uid="b", title="B", url="u2", published="2025-10-09", stats=FeedPostStats(views=15)),
    ]
    posts_feed2 = [
        FeedPost(uid="c", title="C", url="u3", published="2025-10-09", stats=FeedPostStats(views=10)),
        FeedPost(uid="b", title="B", url="u2", published="2025-10-09", stats=FeedPostStats(views=20)),
    ]

    service = TopPostsService(client=DummyClient({"feed1": posts_feed1, "feed2": posts_feed2}), limit=3)
    result = await service.fetch_top_posts(["feed1", "feed2"])

    assert result.total_posts == 4
    assert [post.uid for post in result.posts] == ["b", "c", "a"]

