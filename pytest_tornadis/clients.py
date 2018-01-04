import collections

import tornadis
import tornado

_channels = collections.defaultdict(list)
_data = {}

class MockClient(tornadis.Client):
    channels = _channels
    data = _data

    @tornado.gen.coroutine
    def call(self, *args, **kwargs):
        command = args[0].lower()

        if command == 'publish':
            channel = self.channels[args[1]]
            message = args[2]

            for client in channel:
                client._reply_list.append(message)

            raise tornado.gen.Return(len(channel))

    def is_connected(self):
        return True

    def clear_mock_redis(self):
        self.channels.clear()

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
