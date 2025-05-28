import os
import sys
import argparse
from flask import Flask
from core.p2p import P2P
from api.evaluation import evaluation_bp
from api.network import network_bp
from api.stats import stats_bp
from api.worker import worker_bp

def create_app():
    app = Flask(__name__)
    # attach a P2P instance
    app.p2p = P2P()
    # register your blueprints
    app.register_blueprint(evaluation_bp, url_prefix='/evaluation')
    app.register_blueprint(network_bp,    url_prefix='/network')
    app.register_blueprint(stats_bp,      url_prefix='/stats')
    app.register_blueprint(worker_bp,     url_prefix='/task')
    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Distributed CD Tester: run server or manage nodes"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="start HTTP server")
    run_p.add_argument("--host", default=os.getenv("HOST","127.0.0.1"))
    run_p.add_argument("--port", type=int, default=int(os.getenv("PORT",7000)))

    add_p = sub.add_parser("add-node", help="add a peer to the P2P network")
    add_p.add_argument("--node", required=True, help="ADDRESS:PORT to add")

    rm_p  = sub.add_parser("remove-node", help="remove a peer from the network")
    rm_p.add_argument("--node", required=True, help="ADDRESS:PORT to remove")

    args = parser.parse_args()
    p2p = P2P()

    if args.cmd == "add-node":
        p2p.connected_nodes.add(args.node)
        print(f"Node '{args.node}' added.")
        sys.exit(0)

    if args.cmd == "remove-node":
        p2p.connected_nodes.discard(args.node)
        print(f"Node '{args.node}' removed.")
        sys.exit(0)

    # fallback to running the server
    app = create_app()
    app.run(host=args.host, port=args.port)