from flask import Flask, jsonify, request
import jieba
import numpy as np
from collections import defaultdict
import pymysql
from pymysql import Error

app = Flask(__name__)

class ProductSearchEngine:
    def __init__(self):
        # 初始化MySQL连接配置
        self.db_config = {
            'host': 'localhost',
            'user': 'flask_demo',
            'password': 'flask_demo',
            'database': 'flask_demo'
        }

        # 自定义词典
        self.user_dict = [
            "iPhone13", "Type-C", "充电器", "数据线", "手机壳",
            "华为", "小米", "苹果", "三星", "OPPO",
            "Pro", "Max", "Plus", "5G"
        ]

        for word in self.user_dict:
            jieba.add_word(word)

        self.stop_words = set(['的', '了', '和', '与', '等', '是'])
        self.synonyms = {
            "手机": ["手机", "电话", "移动电话", "智能机"],
            "充电器": ["充电器", "充电头", "电源适配器"],
            "数据线": ["数据线", "充电线", "连接线"],
            "苹果": ["苹果", "Apple", "iPhone"],
            "大豆油":["调和油",""]
        }

        self.index = defaultdict(list)
        self.products = []

        # 初始化数据库并加载商品
        self.init_database()
        self.load_products_from_db()

    def init_database(self):
        """初始化数据库表"""
        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor()

            # 创建商品表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    price DECIMAL(10, 2) NOT NULL
                )
            """)

            conn.commit()
        except Error as e:
            print(f"数据库错误: {e}")
        finally:
            cursor.close()
            conn.close()

    def load_products_from_db(self):
        """从数据库加载商品并建立索引"""
        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            cursor.execute("SELECT * FROM eb_store_spu_test")
            products = cursor.fetchall()

            # 清空现有索引
            self.index.clear()
            self.products.clear()

            # 重新建立索引
            for product in products:
                self.add_product(product)

        except Error as e:
            print(f"数据库错误: {e}")
        finally:
            cursor.close()
            conn.close()

    def preprocess_text(self, text):
        """文本预处理"""
        text = text.lower()
        words = jieba.lcut(text)
        words = [w for w in words if w not in self.stop_words]
        expanded_words = []
        for word in words:
            if word in self.synonyms:
                expanded_words.extend(self.synonyms[word])
            else:
                expanded_words.append(word)
        return expanded_words

    def add_product(self, product):
        """添加商品到索引"""
        product_id = len(self.products)
        self.products.append(product)

        name = product['keyword']
        tokens = self.preprocess_text(name)
        for token in tokens:
            self.index[token].append(product_id)

        for char in name:
            if char not in self.stop_words:
                self.index[char].append(product_id)

    def search(self, query, top_k=1000):
        """搜索商品"""
        query_tokens = self.preprocess_text(query)
        if not query_tokens:
            query_tokens = [query]

        scores = defaultdict(float)

        for token in query_tokens:
            product_ids = self.index.get(token, [])
            if product_ids:
                idf = np.log(len(self.products) / len(product_ids))
                for pid in product_ids:
                    weight = len(token) if len(token) > 1 else 0.5
                    scores[pid] += idf * weight

        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        return [
            {
                'product': self.products[pid],
                'score': score
            }
            for pid, score in results
        ]

# 创建搜索引擎实例
search_engine = ProductSearchEngine()

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': '请提供搜索关键词'}), 400

    results = search_engine.search(query)
    return jsonify({
        'query': query,
        'results': results
    })

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.json
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({'error': '请提供商品名称和价格'}), 400

    try:
        conn = pymysql.connect(**search_engine.db_config)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO products (name, price) VALUES (%s, %s)",
            (data['name'], data['price'])
        )

        conn.commit()

        # 重新加载商品数据
        search_engine.load_products_from_db()

        return jsonify({'message': '商品添加成功'})

    except Error as e:
        return jsonify({'error': f'数据库错误: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':


    # 重新加载商品数据
    search_engine.load_products_from_db()

    # 启动Flask服务
    app.run(host='0.0.0.0',debug=True,port=6632)
