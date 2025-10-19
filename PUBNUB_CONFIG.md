# PubNub Configuration Guide

## Overview

The blockchain application uses PubNub for real-time peer-to-peer communication between nodes. PubNub enables the publish/subscribe pattern that allows blockchain nodes to:

- Broadcast newly mined blocks to all peers
- Share transactions across the network
- Synchronize blockchain state in real-time

## Getting Your PubNub Keys

1. **Create a PubNub Account**
   - Visit [https://www.pubnub.com/](https://www.pubnub.com/)
   - Sign up for a free account (no credit card required)

2. **Create a New App**
   - Once logged in, click "Create New App"
   - Give it a name like "python-blockchain"

3. **Get Your Keys**
   - You'll see two important keys:
     - **Publish Key** - Used to send messages to channels
     - **Subscribe Key** - Used to receive messages from channels
   - Keep these keys handy!

### Using secrets.env (Recommended for Production)

1. **Copy the secrets template:**
   ```bash
   cp env.example .env
   ```

2. **Edit secrets.env and add your keys:**
   ```bash
   PUBNUB_PUBLISH_KEY=pub-c-your-actual-publish-key
   PUBNUB_SUBSCRIBE_KEY=sub-c-your-actual-subscribe-key
   PUBNUB_USER_ID=blockchain-node-1
   ```

### Backend Code

The `backend/pubsub.py` file now reads configuration from environment variables.

## Multi-Node Configuration

When running multiple nodes, ensure each has a unique `PUBNUB_USER_ID`:

```bash
# Node 1 (main)
export PUBNUB_USER_ID=blockchain-node-1
python3 -m backend.app

# Node 2 (peer) - in a different terminal
export PUBNUB_USER_ID=blockchain-node-2
export PEER=True
export PEER_PORT=5001
python3 -m backend.app

# Node 3 (seeded) - in another terminal
export PUBNUB_USER_ID=blockchain-node-3
export PEER=True
export SEED_DATA=True
export PEER_PORT=5002
python3 -m backend.app
```

Each node should have a unique user_id:
- `blockchain-node-1` - Main node
- `blockchain-peer-1` - Peer node
- `blockchain-seed-1` - Seeded node

## PubNub Dashboard Monitoring

You can monitor real-time activity in the PubNub dashboard:

1. Log in to [https://admin.pubnub.com/](https://admin.pubnub.com/)
2. Select your app
3. Go to "Debug Console"
4. Subscribe to your channels to see messages in real-time

This is useful for:
- Debugging connection issues
- Monitoring message flow
- Verifying blockchain synchronization

### Channels Used by This Application

The blockchain application uses the following channels:

- **`BLOCK`** - Broadcasts newly mined blocks to all nodes
- **`TRANSACTION`** - Shares new transactions across the network
- **`TEST`** - Used for testing connectivity (development only)

## Quick Start Guide

### First Time Setup

1. **Get your PubNub keys:**
   - Sign up at https://www.pubnub.com/
   - Create a new app
   - Copy your Publish and Subscribe keys

2. **Configure your environment:**
   ```bash
   # Copy the example file
   cp env.example .env

   # Edit .env with your actual keys
   nano .env
   ```

3. **Run the application:**
   ```bash
   python3 -m backend.app
   ```

### Running Multiple Nodes

To test blockchain synchronization with multiple nodes:

```bash
# Terminal 1 - Main node
export PUBNUB_USER_ID=node-1
python3 -m backend.app

# Terminal 2 - Peer node
export PUBNUB_USER_ID=peer-1
export PEER=True
export PEER_PORT=5001
python3 -m backend.app

```

## Resources

- [PubNub Python SDK Documentation](https://www.pubnub.com/docs/sdks/python)
- [PubNub Publish/Subscribe Tutorial](https://www.pubnub.com/tutorials/python/)
- [PubNub Best Practices](https://www.pubnub.com/docs/general/security/best-practices)
- [PubNub Free Tier Limits](https://www.pubnub.com/pricing/)
