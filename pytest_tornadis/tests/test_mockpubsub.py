"""
    Tests for MockPubSub object.
"""

import pytest
import pytest_tornado

from tornado.ioloop import TimeoutError

from .. import clients

def test_valid_mockpubsub_init():
    client = clients.MockPubSubClient()
    assert not client.channels
    assert client.is_connected()

@pytest.mark.gen_test
@pytest.mark.usefixtures('pubsub_client')
async def test_valid_mockpubsub_pubsub_subscribe_single(pubsub_client):
    assert 'test' not in pubsub_client.channels
    assert not pubsub_client.channels
    await pubsub_client.pubsub_subscribe('test')
    assert 'test' in pubsub_client.channels
    assert len(pubsub_client.channels.keys()) == 1

@pytest.mark.gen_test
@pytest.mark.usefixtures('pubsub_client')
async def test_valid_mockpubsub_pubsub_subscribe_many(pubsub_client):
    assert 'foo' not in pubsub_client.channels
    assert 'bar' not in pubsub_client.channels
    assert not pubsub_client.channels
    await pubsub_client.pubsub_subscribe('foo', 'bar')
    assert 'foo' in pubsub_client.channels
    assert 'bar' in pubsub_client.channels
    assert len(pubsub_client.channels.keys()) == 2

@pytest.mark.gen_test
@pytest.mark.usefixtures('pubsub_client')
async def test_valid_mockpubsub_pubsub_pop_message(pubsub_client):
    await pubsub_client.pubsub_subscribe('test')
    pubsub_client._reply_list.append('test')
    res = await pubsub_client.pubsub_pop_message()
    assert res == 'test'
