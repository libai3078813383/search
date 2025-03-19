import jieba
import numpy as np
from collections import defaultdict


class ProductSearchEngine:
    def __init__(self):
        # 自定义词典
        self.user_dict = [
            "iPhone13", "Type-C", "充电器", "数据线", "手机壳",
            "华为", "小米", "苹果", "三星", "OPPO",
            "Pro", "Max", "Plus", "5G"
        ]

        # 将自定义词典添加到jieba中
        for word in self.user_dict:
            jieba.add_word(word)

        # 停用词
        self.stop_words = set(['的', '了', '和', '与', '等', '是'])

        # 同义词表
        self.synonyms = {
            "手机": ["手机", "电话", "移动电话", "智能机"],
            "充电器": ["充电器", "充电头", "电源适配器"],
            "数据线": ["数据线", "充电线", "连接线"],
            "苹果": ["苹果", "Apple", "iPhone"]
            # "油": ["油", "调和油"]  # 添加油的同义词
        }

        # 倒排索引
        self.index = defaultdict(list)
        # 商品库
        self.products = []

    def preprocess_text(self, text):
        """文本预处理"""
        # 转小写
        text = text.lower()
        # 使用jieba分词
        words = jieba.lcut(text)
        # 去停用词
        words = [w for w in words if w not in self.stop_words]
        # 同义词扩展
        expanded_words = []
        for word in words:
            if word in self.synonyms:
                expanded_words.extend(self.synonyms[word])
            else:
                expanded_words.append(word)

        print(expanded_words)
        return expanded_words

    def add_product(self, product):
        """添加商品到索引"""
        product_id = len(self.products)
        self.products.append(product)

        # 对商品名称分词并建立索引
        name = product['name']
        # 完整词索引
        tokens = self.preprocess_text(name)
        for token in tokens:
            self.index[token].append(product_id)

        # 字符级索引（为了支持单字搜索）
        for char in name:
            if char not in self.stop_words:
                self.index[char].append(product_id)

    def search(self, query, top_k=10):
        """搜索商品"""
        # 对查询词分词
        query_tokens = self.preprocess_text(query)
        if not query_tokens:  # 如果分词结果为空，直接用查询词
            query_tokens = [query]

        # print(f"查询词分词结果: {query_tokens}")  # 调试信息

        # 统计每个商品的匹配分数
        scores = defaultdict(float)

        for token in query_tokens:
            # 获取包含当前词的所有商品
            product_ids = self.index.get(token, [])
            # print(f"Token '{token}' 匹配到的商品ID: {product_ids}")  # 调试信息

            # 计算相似度分数
            if product_ids:
                idf = np.log(len(self.products) / len(product_ids))
                for pid in product_ids:
                    # 根据token长度给予不同的权重
                    weight = len(token) if len(token) > 1 else 0.5
                    scores[pid] += idf * weight

        # 排序并返回top_k个结果
        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        return [
            {
                'product': self.products[pid],
                'score': score
            }
            for pid, score in results
        ]


# 使用示例
if __name__ == "__main__":
    # 初始化搜索引擎
    search_engine = ProductSearchEngine()

    # 添加测试数据
    test_products = [
        {'name': '理然发胶定型喷雾男士速干24H立挺持久强力固定自然哑光海洋香250ml', 'price': 99},
        {'name': '中茶陈香觅古普洱茶礼盒（绿色消费积分标准颁布纪念版）', 'price': 99},
        {'name': '中茶蝴蝶牡丹皇白茶礼盒100g', 'price': 99},
        {'name': '中茶一品香茗（工夫红茶）200g', 'price': 99},

    ]

    for product in test_products:
        search_engine.add_product(product)

    # 打印索引内容（调试用）
    # print("\n索引内容:")
    # for token, product_ids in search_engine.index.items():
    #     print(f"{token}: {product_ids}")

    # 测试搜索
    test_queries = ["和油", "定型水"]

    for query in test_queries:
        print(f"\n搜索: {query}")
        results = search_engine.search(query)
        if results:
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['product']['name']} (得分: {result['score']:.2f})")
        else:
            print("未找到相关商品")
