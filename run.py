from app import create_app
from utils.database import init_db

if __name__ == '__main__':
    # 初始化数据库
    # init_db()

    # 创建并运行应用
    app = create_app()
    app.run(host='0.0.0.0', debug=True, port=7199)
