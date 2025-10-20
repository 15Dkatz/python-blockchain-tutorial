import os
import time
import requests

from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback

from backend.blockchain.block import Block
from backend.blockchain.blockchain import Blockchain
from backend.wallet.transaction import Transaction

pnconfig = PNConfiguration()
pnconfig.publish_key = os.environ.get('PUBNUB_PUBLISH_KEY')
pnconfig.subscribe_key = os.environ.get('PUBNUB_SUBSCRIBE_KEY')
pnconfig.user_id = os.environ.get('PUBNUB_USER_ID', 'blockchain-node-default')

CHANNELS = {
    'TEST': 'TEST',
    'BLOCK': 'BLOCK',
    'TRANSACTION': 'TRANSACTION'
}

class Listener(SubscribeCallback):
    def __init__(self, blockchain, transaction_pool):
        self.blockchain = blockchain
        self.transaction_pool = transaction_pool

    def message(self, pubnub, message_object):
        print(f'\n-- Channel: {message_object.channel} | Message: {message_object.message}')

        if message_object.channel == CHANNELS['BLOCK']:
            block = Block.from_json(message_object.message)
            potential_chain = self.blockchain.chain[:]
            potential_chain.append(block)

            try:
                self.blockchain.replace_chain(potential_chain)

                self.transaction_pool.clear_blockchain_transactions(
                    self.blockchain
                )

                print('\n -- Successfully replaced the local chain')
            except Exception as e:
                print(f'\n -- Did not replace chain: {e}')

                # If we can't validate the block, try to sync the full blockchain
                # This handles cases where we're missing previous blocks
                self.sync_blockchain()

        elif message_object.channel == CHANNELS['TRANSACTION']:
            transaction = Transaction.from_json(message_object.message)
            self.transaction_pool.set_transaction(transaction)
            print('\n -- Set the new transaction in the transaction pool')
    
    def sync_blockchain(self):
        """
        Synchronize the local blockchain with the root node.
        This is called when we receive a block we can't validate.
        """
        try:
            # Get the root backend host (main node)
            root_host = os.environ.get('ROOT_BACKEND_HOST', 'localhost')
            root_port = os.environ.get('ROOT_PORT', '5050')

            print(f'\n -- Attempting to sync blockchain from {root_host}:{root_port}')

            # Request the full blockchain from the root node
            response = requests.get(f'http://{root_host}:{root_port}/blockchain')
            result_blockchain = Blockchain.from_json(response.json())

            # Replace our local chain with the synchronized chain
            self.blockchain.replace_chain(result_blockchain.chain)

            print(f'\n -- Successfully synchronized! Chain length: {len(self.blockchain.chain)}')
        except Exception as e:
            print(f'\n -- Could not synchronize blockchain: {e}')

class PubSub():
    """
    Handles the publish/subscribe layer of the application.
    Provides communication between the nodes of the blockchain network.
    """
    def __init__(self, blockchain, transaction_pool):
        self.pubnub = PubNub(pnconfig)
        self.pubnub.subscribe().channels(CHANNELS.values()).execute()
        self.pubnub.add_listener(Listener(blockchain, transaction_pool))

    def publish(self, channel, message):
        """
        Publish the message object to the channel.
        """
        try:
            result = self.pubnub.publish().channel(channel).message(message).sync()
            print(f'\n-- Published to {channel}: {result.status.is_error()}')
        except Exception as e:
            print(f'\n-- Error publishing to {channel}: {e}')

    def broadcast_block(self, block):
        """
        Broadcast a block object to all nodes.
        """
        self.publish(CHANNELS['BLOCK'], block.to_json())

    def broadcast_transaction(self, transaction):
        """
        Broadcast a transaction to all nodes.
        """
        self.publish(CHANNELS['TRANSACTION'], transaction.to_json())

def main():
    pubsub = PubSub()

    time.sleep(1)

    pubsub.publish(CHANNELS['TEST'], { 'foo': 'bar' })

if __name__ == '__main__':
    main()
