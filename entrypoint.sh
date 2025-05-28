#!/bin/sh
HOST_IP=$(hostname -I | awk '{print $1}')
export NODE_ADDRESS=${HOST_IP}:${PORT:-7000}
export SEED_NODES=${HOST_IP}:7000
exec flask run --host=0.0.0.0 --port=${PORT:-7000}