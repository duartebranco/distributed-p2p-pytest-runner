from flask import Flask
from api.evaluation import evaluation_bp
from api.stats import stats_bp
from api.network import network_bp
from core.p2p import P2P
from api.worker import worker_bp
import os

def create_app():
    app = Flask(__name__)
    app.config['NODE_ADDRESS'] = os.getenv('NODE_ADDRESS', '')
    app.p2p = P2P()

    # Register blueprints for API endpoints
    app.register_blueprint(evaluation_bp, url_prefix='/evaluation')
    app.register_blueprint(stats_bp, url_prefix='/stats')
    app.register_blueprint(network_bp, url_prefix='/network')
    app.register_blueprint(worker_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=7000)