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

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_hmset(mock_client):
    with pytest.raises(ValueError):
        await mock_client.call('HMSET', 'test')     # Not enough arguments.

    with pytest.raises(ValueError):
        await mock_client.call('HMSET', 'test', 'foo')     # Not enough arguments.

    assert 'test' not in mock_client.data
    await mock_client.call('HMSET', 'test', 'foo', 'bar')
    assert mock_client.data['test'] == (clients.RedisCommands.HMSET, {'foo': 'bar'})

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_no_command(mock_client):
    with pytest.raises(ValueError):
        await mock_client.call('NOTACOMMAND')

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_hget(mock_client):
    with pytest.raises(ValueError):
        await mock_client.call('HGET', 'TEST')   # Too short

    with pytest.raises(ValueError):
        await mock_client.call('HGET', 'TEST', 'foo', 'bar')   # Too long

    # No key
    assert 'test' not in mock_client.data
    result = await mock_client.call('HGET', 'test', 'foo')
    assert result is None

    # No field
    mock_client.data['test'] = (clients.RedisCommands.HMSET, {'notfoo': 'bar'})
    result = await mock_client.call('HGET', 'test', 'foo')
    assert result is None

    # Success
    mock_client.data['test'] = (clients.RedisCommands.HMSET, {'foo': 'bar'})
    result = await mock_client.call('HGET', 'test', 'foo')
    assert result is 'bar'

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_hgetall(mock_client):
    with pytest.raises(ValueError):
        await mock_client.call('HGETALL')   # Too short

    with pytest.raises(ValueError):
        await mock_client.call('HGETALL', 'TEST', 'foo')   # Too long

    # No key
    assert 'test' not in mock_client.data
    result = await mock_client.call('HGETALL', 'test')
    assert result is None

    # Success
    mock_client.data['test'] = (clients.RedisCommands.HMSET, {'foo': 'bar'})
    result = await mock_client.call('HGETALL', 'test')
    assert result == {'foo': 'bar'}
