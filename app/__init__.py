from flask import Flask
from app.routes.search_routes import search_bp
from utils.logger_handler import logger
def create_app():
    app = Flask(__name__)
    app.register_blueprint(search_bp)
    # 初始化日志处理器
    logger.init_app(app)
    return app
