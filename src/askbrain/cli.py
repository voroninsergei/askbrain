from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import click

from askbrain.clients.tilda import TildaFeedClient
from askbrain.config import get_settings
from askbrain.services.top_posts import TopPostsService
from askbrain.utils.json import dump_to_file, serialize_datetime


@click.group()
def app() -> None:
    """Инструменты Askbrain."""


@app.command("fetch-top")
@click.option("--output", default="data/top_posts.json", help="Путь к основному JSON", show_default=True)
@click.option("--meta-output", default="data/top_posts_meta.json", help="Путь к метаданным", show_default=True)
def fetch_top(output: str, meta_output: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    asyncio.run(_fetch_top_impl(Path(output), Path(meta_output)))


def main() -> None:
    app()


async def _fetch_top_impl(output: Path, meta_output: Path) -> None:
    settings = get_settings()
    async with TildaFeedClient(settings=settings) as client:
        service = TopPostsService(client=client, limit=10, concurrency=settings.tilda_concurrency)
        result = await service.fetch_top_posts(settings.tilda_feed_uids)

    posts_data = {
        "overall_top": [post.model_dump(mode="json") for post in result.posts],
        "by_category": {
            category: [post.model_dump(mode="json") for post in posts]
            for category, posts in result.posts_by_category.items()
        },
    }
    dump_to_file(posts_data, output)

    dump_to_file(
        {
            "fetched_at": serialize_datetime(result.fetched_at),
            "source_feeds": list(result.source_feeds),
            "total_posts": result.total_posts,
            "result_posts": len(result.posts),
            "categories": result.category_stats,
        },
        meta_output,
    )


if __name__ == "__main__":
    main()

