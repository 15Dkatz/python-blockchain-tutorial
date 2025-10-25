import os
import requests
import random
import threading
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST, before any other backend imports
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json

from backend.blockchain.blockchain import Blockchain
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction
from backend.wallet.transaction_pool import TransactionPool
from backend.pubsub import PubSub

app = Flask(__name__)
CORS(app, resources={ r'/*': { 'origins': 'http://localhost:3000' } })

def json_response(data, status=200):
    """
    Create a JSON response that preserves large integers.
    Flask's default jsonify converts large ints to floats, which breaks
    cryptographic signatures. This function ensures integers are preserved.
    """
    return Response(
        json.dumps(data, separators=(',', ':')),
        status=status,
        mimetype='application/json'
    )
blockchain = Blockchain()
wallet = Wallet(blockchain)
transaction_pool = TransactionPool()
pubsub = PubSub(blockchain, transaction_pool)

@app.route('/')
def route_default():
    return 'Welcome to the blockchain'

@app.route('/blockchain')
def route_blockchain():
    return json_response(blockchain.to_json())

@app.route('/blockchain/range')
def route_blockchain_range():
    # http://localhost:5050/blockchain/range?start=2&end=5
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    return jsonify(blockchain.to_json()[::-1][start:end])

@app.route('/blockchain/length')
def route_blockchain_length():
    return jsonify(len(blockchain.chain))

@app.route('/blockchain/mine')
def route_blockchain_mine():
    transaction_data = transaction_pool.transaction_data()
    transaction_data.append(Transaction.reward_transaction(wallet).to_json())
    blockchain.add_block(transaction_data)
    block = blockchain.chain[-1]
    pubsub.broadcast_block(block)
    transaction_pool.clear_blockchain_transactions(blockchain)

    return json_response(block.to_json())

@app.route('/wallet/transact', methods=['POST'])
def route_wallet_transact():
    transaction_data = request.get_json()
    transaction = transaction_pool.existing_transaction(wallet.address)

    if transaction:
        transaction.update(
            wallet,
            transaction_data['recipient'],
            transaction_data['amount']
        )
    else:
        transaction = Transaction(
            wallet,
            transaction_data['recipient'],
            transaction_data['amount']
        )

    pubsub.broadcast_transaction(transaction)
    transaction_pool.set_transaction(transaction)

    return jsonify(transaction.to_json())

@app.route('/wallet/info')
def route_wallet_info():
    return jsonify({ 'address': wallet.address, 'balance': wallet.balance })

@app.route('/known-addresses')
def route_known_addresses():
    known_addresses = set()

    for block in blockchain.chain:
        for transaction in block.data:
            known_addresses.update(transaction['output'].keys())

    return jsonify(list(known_addresses))

@app.route('/transactions')
def route_transactions():
    return jsonify(transaction_pool.transaction_data())

ROOT_PORT = 5050
PORT = ROOT_PORT

if os.environ.get('PEER') == 'True':
    PORT = random.randint(5051, 6000)

    # In Docker, use service name instead of localhost
    ROOT_HOST = os.environ.get('ROOT_BACKEND_HOST', 'localhost')
    result = requests.get(f'http://{ROOT_HOST}:{ROOT_PORT}/blockchain')
    result_blockchain = Blockchain.from_json(result.json())

    try:
        blockchain.replace_chain(result_blockchain.chain)
        print('\n -- Successfully synchronized the local chain')
    except Exception as e:
        print(f'\n -- Error synchronizing: {e}')

if os.environ.get('SEED_DATA') == 'True':
    for i in range(10):
        blockchain.add_block([
            Transaction(Wallet(), Wallet().address, random.randint(2, 50)).to_json(),
            Transaction(Wallet(), Wallet().address, random.randint(2, 50)).to_json()
        ])

    for i in range(3):
        transaction = Transaction(Wallet(), Wallet().address, random.randint(2, 50))
        pubsub.broadcast_transaction(transaction)
        transaction_pool.set_transaction(transaction)

def poll_root_blockchain():
    """
    Poll the root blockchain every 15 seconds and attempt to sync.
    This runs in a background thread when POLL_ROOT environment variable is True.
    """
    while True:
        try:
            # Get the root host from environment, fallback to localhost
            root_host = os.environ.get('ROOT_BACKEND_HOST', 'localhost')
            root_port = ROOT_PORT
            
            # Fetch blockchain from root host
            response = requests.get(f'http://{root_host}:{root_port}/blockchain', timeout=10)
            response.raise_for_status()
            
            # Parse the blockchain
            result_blockchain = Blockchain.from_json(response.json())
            
            # Attempt to replace the local chain with the root chain
            blockchain.replace_chain(result_blockchain.chain)
            print(f'\n -- Successfully synchronized with root blockchain at {root_host}:{root_port}')
            
        except requests.exceptions.RequestException as e:
            print(f'\n -- Error fetching blockchain from root: {e}')
        except Exception as e:
            print(f'\n -- Error synchronizing with root blockchain: {e}')
        
        # Wait 15 seconds before next poll
        time.sleep(15)

if os.environ.get('POLL_ROOT') == 'True':
    # Start the polling thread
    poll_thread = threading.Thread(target=poll_root_blockchain, daemon=True)
    poll_thread.start()
    print('\n -- Started polling root blockchain every 15 seconds')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)

