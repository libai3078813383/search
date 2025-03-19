import jieba
import jieba.analyse
from collections import defaultdict
import numpy as np


class ProductSearch:
    def __init__(self):
        # 添加自定义词典
        self.user_dict = [
            "iPhone13", "Type-C", "充电器", "数据线",
            "华为", "小米", "苹果", "三星"
        ]
        for word in self.user_dict:
            jieba.add_word(word)

        # 停用词
        self.stop_words = set(['的', '了', '和'])

        # 同义词表
        self.synonyms = {
            "手机": ["手机", "电话", "移动电话"],
            "充电器": ["充电器", "充电头"],
            "数据线": ["数据线", "充电线"],
        }

        self.products = []
        self.index = defaultdict(list)

    def segment(self, text):
        """分词处理"""
        # jieba分词
        words = jieba.cut(text)
        # 去停用词
        words = [w for w in words if w not in self.stop_words]
        # 同义词扩展
        expanded = []
        for w in words:
            if w in self.synonyms:
                expanded.extend(self.synonyms[w])
            else:
                expanded.append(w)
        return expanded

    def extract_keywords(self, text):
        """提取关键词"""
        # 使用TF-IDF提取关键词
        keywords = jieba.analyse.extract_tags(
            text,
            topK=5,
            withWeight=True
        )
        return keywords

    def add_product(self, product):
        """添加商品到索引"""
        pid = len(self.products)
        self.products.append(product)

        # 对商品名称分词
        tokens = self.segment(product['name'])

        # 建立倒排索引
        for token in tokens:
            self.index[token].append(pid)

        # 提取关键词和权重
        keywords = self.extract_keywords(product['name'])
        product['keywords'] = dict(keywords)

    def search(self, query, top_k=5):
        """搜索商品"""
        # 对查询分词
        query_tokens = self.segment(query)

        # 计算相关度分数
        scores = defaultdict(float)

        # 基于词频的相关度计算
        for token in query_tokens:
            if token in self.index:
                idf = np.log(len(self.products) / len(self.index[token]))
                for pid in self.index[token]:
                    scores[pid] += idf

        # 基于关键词权重的相关度计算
        query_keywords = dict(self.extract_keywords(query))
        for pid in scores:
            product = self.products[pid]
            for word, weight in query_keywords.items():
                if word in product['keywords']:
                    scores[pid] += weight * product['keywords'][word]

        # 排序返回结果
        results = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

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
    search = ProductSearch()

    # 添加测试商品
    test_products = [
        {'name': 'iPhone13 Pro Max 手机壳', 'price': 99},
        {'name': 'Type-C 快充数据线', 'price': 29},
        {'name': '苹果手机充电器 20W', 'price': 149},
        {'name': '华为手机 5G', 'price': 4999},
        {'name': '小米充电器 33W', 'price': 69},
    ]

    for product in test_products:
        search.add_product(product)

    # 测试搜索
    query = "苹果充电器"
    results = search.search(query)

    print(f"搜索: {query}")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['product']['name']} (得分: {result['score']:.2f})")

