import pytest


@pytest.fixture
def mock_settings(mocker):
    settings = mocker.Mock()
    settings.origin_host = "https://askbrain.ru"
    settings.tilda_feed_uids = ("824854191681",)
    settings.tilda_rec_id = "1396561121"
    settings.tilda_default_size = 100
    settings.tilda_concurrency = 2
    return settings

