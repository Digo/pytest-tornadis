import collections
import datetime
import enum

import tornadis
import tornado

_channels = collections.defaultdict(list)
_data = {}

class RedisCommands(enum.Enum):
    PUBLISH = 'publish'
    DEL = 'del'
    GET = 'get'
    SET = 'set'
    SETEX = 'setex'
    HMSET = 'hmset'
    HGET = 'hget'
    HGETALL = 'hgetall'
    HSET = 'hset'
    EXPIRE = 'expire'
    PERSIST = 'persist'
    RPUSH = 'rpush'
    LRANGE = 'lrange'

class MockClient(tornadis.Client):
    channels = _channels
    data = _data

    @tornado.gen.coroutine
    def call(self, *args, **kwargs):
        command = RedisCommands(args[0].lower())

        if command == RedisCommands.PUBLISH:
            channel = self.channels[args[1]]
            message = args[2]

            for client in channel:
                client._reply_list.append(message)

            raise tornado.gen.Return(len(channel))
        elif command == RedisCommands.DEL:
            successful = 0
            for key in args[1:]:
                if key in self.data:
                    del self.data[key]
                    successful += 1

            return successful
        elif command == RedisCommands.GET:
            key = args[1]
            if key not in self.data:
                raise tornado.gen.Return(None)

            val = self.data[key]
            if val[0] == RedisCommands.SETEX and datetime.datetime.utcnow() > val[2]:
                del self.data[key]
                raise tornado.gen.Return(None)

            return val[1]
        elif command == RedisCommands.SETEX:
            key = args[1]
            ttl = datetime.datetime.utcnow() + datetime.timedelta(seconds=args[2])
            data = args[3]

            self.data[key] = (RedisCommands.SETEX, data, ttl)
        elif command == RedisCommands.SET:
            key = args[1]
            data = args[2]

            self.data[key] = (RedisCommands.SET, data)
        elif command == RedisCommands.HMSET:
            arg_len = len(args) - 2
            if arg_len % 2 or arg_len < 1:
                raise ValueError('Invalid parameters.')

            key = args[1]
            data_dict = yield self.call(RedisCommands.HGETALL.value, key)
            if not isinstance(data_dict, dict):
                data_dict = {}

            dict_args = zip(*[iter(args[2:])]*2)
            for dkey, dval in dict_args:
                data_dict[dkey] = dval

            self.data[key] = (RedisCommands.HMSET, data_dict)
            return 'OK'.encode('utf-8')
        elif command == RedisCommands.HGET:
            if len(args) != 3:
                raise ValueError('Invalid parameters.')

            key = args[1]
            redis_dict = yield self.call(RedisCommands.GET.value, key)
            if redis_dict is None:
                return redis_dict

            field = args[2]
            if field not in redis_dict:
                raise tornado.gen.Return(None)
            return redis_dict[field]
        elif command == RedisCommands.HGETALL:
            if len(args) != 2:
                raise ValueError('Invalid parameters.')

            key = args[1]
            redis_dict = yield self.call(RedisCommands.GET.value, key)
            return redis_dict
        elif command == RedisCommands.HSET:
            if len(args) != 4:
                raise ValueError('Invalid parameters.')

            key = args[1]
            field = args[2]
            value = args[3]
            result = yield self.call(RedisCommands.GET.value, key)

            yield self.call(RedisCommands.HMSET.value, key, field, value)
            return 1 if not isinstance(result, dict) or field not in result else 0
        elif command == RedisCommands.EXPIRE:
            if len(args) != 3:
                raise ValueError('Invalid parameters.')

            key = args[1]
            result = yield self.call(RedisCommands.GET.value, key)
            if result is None:
                return 0

            ttl = args[2]
            yield self.call(RedisCommands.SETEX.value, key, ttl, result)
            return 1
        elif command == RedisCommands.PERSIST:
            key = args[1]
            result = yield self.call(RedisCommands.GET.value, key)
            if result is None:
                return 0

            yield self.call(RedisCommands.SET.value, key, result)
            return 1
        elif command == RedisCommands.RPUSH:
            key = args[1]
            result = yield self.call(RedisCommands.GET.value, key)
            if not isinstance(result, list):
                result = []

            if len(args) < 3:
                return len(result)
            result.extend(args[2:])
            yield self.call(RedisCommands.SET.value, key, result)
            return len(result)
        elif command == RedisCommands.LRANGE:
            if len(args) < 3:
                raise ValueError('Invalid arguments')

            key = args[1]
            start_idx = int(args[2])
            stop_idx = -1 if len(args) < 4 else int(args[3])
            result = yield self.call(RedisCommands.GET.value, key)

            if result is None or start_idx > len(result):
                return []

            if stop_idx == len(result) or stop_idx == -1:
                stop_idx = len(result)
            return result[start_idx: stop_idx + 1]

    def is_connected(self):
        return True

    def clear_mock_redis(self):
        self.channels.clear()
        self.data.clear()

class MockPubSubClient(tornadis.PubSubClient, MockClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reply_list = []

    @tornado.gen.coroutine
    def pubsub_subscribe(self, *args):
        for channel in args:
            self.channels[channel].append(self)

        raise tornado.gen.Return(len(args))

    @tornado.gen.coroutine
    def pubsub_unsubscribe(self, *args):
        for channel in args:
            self.channels[channel].remove(self)

        raise tornado.gen.Return(len(args))

    @tornado.gen.coroutine
    def pubsub_pop_message(self, *args, **kwargs):
        reply = None

        try:
            reply = self._reply_list.pop(0)
            raise tornado.gen.Return(reply)
        except IndexError:
            pass

        yield self._condition.wait()
        try:
            reply = self._reply_list.pop(0)
        except IndexError:
            pass

        raise tornado.gen.Return(reply)
