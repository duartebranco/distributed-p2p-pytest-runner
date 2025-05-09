from flask import Flask
from api.evaluation import evaluation_bp
from api.stats import stats_bp
from api.network import network_bp

def create_app():
    app = Flask(__name__)

    # Register blueprints for API endpoints
    app.register_blueprint(evaluation_bp, url_prefix='/evaluation')
    app.register_blueprint(stats_bp, url_prefix='/stats')
    app.register_blueprint(network_bp, url_prefix='/network')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)