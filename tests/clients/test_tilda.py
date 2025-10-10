import httpx
import pytest
import respx

from askbrain.clients.tilda import TildaFeedClient


@pytest.fixture
def settings(monkeypatch):
    class DummySettings:
        origin_host = "https://askbrain.ru"
        tilda_feed_uids = ("824854191681",)
        tilda_default_size = 2
        tilda_concurrency = 2

    dummy = DummySettings()
    monkeypatch.setattr("askbrain.clients.tilda.get_settings", lambda: dummy)
    return dummy


@pytest.mark.asyncio
async def test_fetch_all_posts_handles_pagination(settings):
    client = httpx.AsyncClient()
    tilda_client = TildaFeedClient(settings=settings, client=client)

    first_response = {
        "feeduid": "824854191681",
        "posts": [
            {
                "uid": "post1",
                "title": "Post 1",
                "url": "https://example.com/post1",
                "published": "2025-10-09 05:00:00",
                "stats": {"views": 5, "likes": 0},
            }
        ],
        "slice": 1,
        "total": 2,
        "nextslice": 2,
    }

    second_response = {
        "feeduid": "824854191681",
        "posts": [
            {
                "uid": "post2",
                "title": "Post 2",
                "url": "https://example.com/post2",
                "published": "2025-10-09 06:00:00",
                "stats": {"views": 10, "likes": 1},
            }
        ],
        "slice": 2,
        "total": 2,
        "nextslice": None,
    }

    with respx.mock(assert_all_called=True) as route:
        route.get("https://feeds.tildaapi.com/api/getfeed/").mock(
            side_effect=[
                httpx.Response(200, json=first_response),
                httpx.Response(200, json=second_response),
            ]
        )

        posts = await tilda_client.fetch_all_posts("824854191681")

    assert len(posts) == 2
    assert posts[0].uid == "post1"
    assert posts[1].uid == "post2"
    await client.aclose()

