import time
import uuid

from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD, MINING_REWARD_INPUT

class Transaction:
    """
    Document of an exchange in currency from a sender to one
    or more recipients.
    """
    def __init__(
        self,
        sender_wallet=None,
        recipient=None,
        amount=None,
        id=None,
        output=None,
        input=None
    ):
        self.id = id or str(uuid.uuid4())[0:8]
        self.output = output or self.create_output(
            sender_wallet,
            recipient,
            amount
        )
        self.input = input or self.create_input(sender_wallet, self.output)

    def create_output(self, sender_wallet, recipient, amount):
        """
        Structure the output data for the transaction.
        """
        if amount > sender_wallet.balance:
            raise Exception('Amount exceeds balance')

        output = {}
        output[recipient] = amount
        output[sender_wallet.address] = sender_wallet.balance - amount

        return output

    def create_input(self, sender_wallet, output):
        """
        Structure the input data for the transaction.
        Sign the transaction and include the sender's public key and address
        """
        return {
            'timestamp': time.time_ns(),
            'amount': sender_wallet.balance,
            'address': sender_wallet.address,
            'public_key': sender_wallet.public_key,
            'signature': sender_wallet.sign(output)
        }

    def update(self, sender_wallet, recipient, amount):
        """
        Update the transaction with an existing or new recipient.
        """
        if amount > self.output[sender_wallet.address]:
            raise Exception('Amount exceeds balance')

        if recipient in self.output:
            self.output[recipient] = self.output[recipient] + amount
        else:
            self.output[recipient] = amount

        self.output[sender_wallet.address] = \
            self.output[sender_wallet.address] - amount

        self.input = self.create_input(sender_wallet, self.output)

    def to_json(self):
        """
        Serialize the transaction.
        Convert large signature integers to strings to prevent float conversion in JSON.
        """
        transaction_dict = self.__dict__.copy()

        if self.input != None and isinstance(self.input, dict) and 'signature' in self.input:
            transaction_dict = {
                'id': self.id,
                'output': self.output.copy(),
                'input': self.input.copy()
            }
            # Convert signature tuple/list to string representations
            sig = self.input['signature']
            transaction_dict['input']['signature'] = [str(sig[0]), str(sig[1])]
        
        return transaction_dict

    @staticmethod
    def from_json(transaction_json):
        """
        Deserialize a transaction's json representation back into a
        Transaction instance.
        Convert signature strings back to integers.
        """
        # Make a copy to avoid mutating the original
        transaction_data = transaction_json.copy()
        
        # If there's a signature, convert strings back to integers
        if 'input' in transaction_data and transaction_data['input'] is not None:
            if isinstance(transaction_data['input'], dict) and 'signature' in transaction_data['input']:
                sig = transaction_data['input']['signature']
                # Convert string representations back to integers
                if isinstance(sig[0], str):
                    transaction_data['input'] = transaction_data['input'].copy()
                    transaction_data['input']['signature'] = [int(sig[0]), int(sig[1])]
        
        return Transaction(**transaction_data)

    @staticmethod
    def is_valid_transaction(transaction):
        """
        Validate a transaction.
        Raise an exception for invalid transactions.
        """
        if transaction.input == MINING_REWARD_INPUT:
            if list(transaction.output.values()) != [MINING_REWARD]:
                raise Exception('Invalid mining reward')
            return

        output_total = sum(transaction.output.values())

        if transaction.input['amount'] != output_total:
            raise Exception('Invalid transaction output values')

        if not Wallet.verify(
            transaction.input['public_key'],
            transaction.output,
            transaction.input['signature']
        ):
            raise Exception('Invalid signature')

    @staticmethod
    def reward_transaction(miner_wallet):
        """
        Generate a reward transaction that award the miner.
        """
        output = {}
        output[miner_wallet.address] = MINING_REWARD

        return Transaction(input=MINING_REWARD_INPUT, output=output)

def main():
    transaction = Transaction(Wallet(), 'recipient', 15)
    print(f'transaction.__dict__: {transaction.__dict__}')

    transaction_json = transaction.to_json()
    restored_transaction = Transaction.from_json(transaction_json)
    print(f'restored_transaction.__dict__: {restored_transaction.__dict__}')

if __name__ == '__main__':
    main()
