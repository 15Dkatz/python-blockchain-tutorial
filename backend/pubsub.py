import time

from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback

pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-666638f6-ec63-11e9-b715-9abbdb5d0da2'
pnconfig.publish_key = 'pub-c-82bf7695-ce5e-4bc5-9cd9-a8f8147dc2a8'
pubnub = PubNub(pnconfig)

TEST_CHANNEL = 'TEST_CHANNEL'

pubnub.subscribe().channels([TEST_CHANNEL]).execute()

class Listener(SubscribeCallback):
    def message(self, pubnub, message_object):
        print(f'\n-- Incoming message_object: {message_object}')


pubnub.add_listener(Listener())

def main():
    time.sleep(1)

    pubnub.publish().channel(TEST_CHANNEL).message({ 'foo': 'bar' }).sync()

if __name__ == '__main__':
    main()
