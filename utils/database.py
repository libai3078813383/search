import pymysql
from config.config import Config


def get_db_connection():
    return pymysql.connect(**Config.MYSQL_CONFIG)


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 创建商品表
        # cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS products (
        #         id INT AUTO_INCREMENT PRIMARY KEY,
        #         name VARCHAR(255) NOT NULL,
        #         price DECIMAL(10, 2) NOT NULL
        #     )
        # """)

        # 创建同义词表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS synonyms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                word VARCHAR(50) NOT NULL,
                synonym VARCHAR(50) NOT NULL
            )
        """)

        conn.commit()
    finally:
        cursor.close()
        conn.close()
