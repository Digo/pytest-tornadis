"""
    Tests for MockPubSub object.
"""

import pytest
import pytest_tornado

from .. import clients

def test_valid_mockclient_init():
    client = clients.MockClient()
    assert not client.channels
    assert client.is_connected()

@pytest.mark.gen_test
@pytest.mark.usefixtures('pubsub_client', 'mock_client')
async def test_valid_mockclient_call_publish(pubsub_client, mock_client):
    await pubsub_client.pubsub_subscribe('test')
    assert not pubsub_client._reply_list
    assert len(pubsub_client.channels['test']) == 1
    assert pubsub_client.channels['test'][0] == pubsub_client

    mock_client.call('PUBLISH', 'test', 'message')
    val = await pubsub_client.pubsub_pop_message()
    assert val == 'message'
