#!/bin/sh

export NODE_ADDRESS=${HOST_IP}:${PORT:-7000}
export SEED_NODES=${SEED_NODES:-${HOST_IP}:7000}

echo "HOST_IP: $HOST_IP"
echo "NODE_ADDRESS: $NODE_ADDRESS"
echo "SEED_NODES: $SEED_NODES"

exec flask run --host=0.0.0.0 --port=${PORT:-7000}