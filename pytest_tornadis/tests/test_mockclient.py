"""
    Tests for MockPubSub object.
"""

import time

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
    result = await mock_client.call('HMSET', 'test', 'foo', 'bar')
    assert result == 'OK'.encode('utf-8')
    assert mock_client.data['test'] == (clients.RedisCommands.HMSET, {'foo': 'bar'})

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_no_command(mock_client):
    with pytest.raises(ValueError):
        await mock_client.call('NOTACOMMAND')

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_get(mock_client):
    assert 'test' not in mock_client.data
    result = await mock_client.call('GET', 'test')
    assert result is None

    # Expired
    await mock_client.call('SETEX', 'test', 1, 'foo')
    assert 'test' in mock_client.data
    time.sleep(5)
    result = await mock_client.call('GET', 'test')
    assert result is None

    # Success
    mock_client.data['test'] = (clients.RedisCommands.SET, 'foo')
    result = await mock_client.call('GET', 'test')
    assert result == 'foo'

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_set(mock_client):
    assert 'test' not in mock_client.data
    result = await mock_client.call('SET', 'test', 'foo')
    assert mock_client.data['test'] == (clients.RedisCommands.SET, 'foo')

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

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_hset(mock_client):
    with pytest.raises(ValueError):
        await mock_client.call('HSET', 'test', 'foo')   # Too short

    with pytest.raises(ValueError):
        await mock_client.call('HSET', 'TEST', 'foo', 'bar', 'foobar')   # Too long

    # No key
    assert 'test' not in mock_client.data
    result = await mock_client.call('HSET', 'test', 'foo', 'bar')
    assert result == 1

    # Success
    mock_client.data['test'] = (clients.RedisCommands.HMSET, {})
    result = await mock_client.call('HSET', 'test', 'foo', 'bar')
    assert result == 0

    result = await mock_client.call('HGETALL', 'test')
    assert result == {'foo': 'bar'}

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_expire(mock_client):
    with pytest.raises(ValueError):
        await mock_client.call('EXPIRE', 'test')   # Too short

    with pytest.raises(ValueError):
        await mock_client.call('EXPIRE', 'TEST', 'foo', 'bar')   # Too long

    # No key
    assert 'test' not in mock_client.data
    result = await mock_client.call('EXPIRE', 'test', 1)
    assert result is 0

    # Success
    mock_client.data['test'] = (clients.RedisCommands.SET, 'foo')
    result = await mock_client.call('EXPIRE', 'test', 1)
    assert result == 1
    time.sleep(5)
    result = await mock_client.call('GET', 'test')
    assert result is None

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_del(mock_client):
    mock_client.data['test'] = (clients.RedisCommands.SET, 'foo')
    await mock_client.call('DEL', 'test')
    assert 'test' not in mock_client.data

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_persist(mock_client):
    # No key
    assert 'test' not in mock_client.data
    result = await mock_client.call('PERSIST', 'test', 1)
    assert result is 0

    # Success
    await mock_client.call('SETEX', 'test', 5, 'foo')
    result = await mock_client.call('PERSIST', 'test')
    assert result == 1
    time.sleep(7)
    assert 'test' in mock_client.data

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_RPUSH(mock_client):
    # No values
    assert 'test' not in mock_client.data
    result = await mock_client.call('RPUSH', 'test')
    assert result == 0

    # New List
    assert 'test' not in mock_client.data
    result = await mock_client.call('RPUSH', 'test', 'foo')
    assert result == 1
    assert mock_client.data['test'] == (clients.RedisCommands.SET, ['foo'])

    # Append List
    result = await mock_client.call('RPUSH', 'test', 'bar', 'foobar')
    assert result == 3
    assert mock_client.data['test'] == (clients.RedisCommands.SET, ['foo', 'bar', 'foobar'])

@pytest.mark.gen_test
@pytest.mark.usefixtures('mock_client')
async def test_mockclient_lrange(mock_client):
    # Invalid values
    with pytest.raises(ValueError):
        await mock_client.call('LRANGE', 'test')

    # Success
    assert 'test' not in mock_client.data
    result = await mock_client.call('LRANGE', 'test', 0)
    assert result == []

    mock_client.data['test'] = (clients.RedisCommands.SET, ['foo', 'bar', 'foobar'])
    assert 'test' in mock_client.data
    result = await mock_client.call('LRANGE', 'test', 4)
    assert result == []

    result = await mock_client.call('LRANGE', 'test', 0)
    assert result == ['foo', 'bar', 'foobar']

    result = await mock_client.call('LRANGE', 'test', 0, 5)
    assert result == ['foo', 'bar', 'foobar']

    result = await mock_client.call('LRANGE', 'test', 0, 1)
    assert result == ['foo', 'bar']
