import pytest

from .. import clients

@pytest.fixture
def pubsub_client():
    client = clients.MockPubSubClient()
    yield client
    client.clear_mock_redis()

@pytest.fixture
def mock_client():
    client = clients.MockClient()
    yield client
    client.clear_mock_redis()
