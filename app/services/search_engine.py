import math

import jieba
import jieba.posseg as pseg
import numpy as np
import pymysql
from collections import defaultdict
from utils.database import get_db_connection
from config.config import Config
import re

class ProductSearchEngine:
    def __init__(self):
        self.index = defaultdict(list)
        self.products = []
        self.synonyms = self._load_synonyms()

        # 初始化jieba分词
        for word in Config.USER_DICT:
            jieba.add_word(word)

        self.load_products_from_db()

    def _load_synonyms(self):
        """从数据库加载同义词"""
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("SELECT word, synonym FROM synonyms")
            synonyms_data = cursor.fetchall()

            synonyms = defaultdict(list)
            for row in synonyms_data:
                synonyms[row['word']].append(row['synonym'])
            return synonyms
        finally:
            cursor.close()
            conn.close()

    def load_products_from_db(self):
        """从数据库加载商品并建立索引"""
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("SELECT S.spu_id,S.product_id,S.store_name,Z.zone_rule_id FROM `eb_store_spu` `S` LEFT JOIN `eb_store_product` `P` ON `S`.`product_id` = `P`.`product_id` LEFT JOIN `eb_store_product_zone` `Z` ON `S`.`product_id` = `Z`.`product_id` WHERE `P`.`mer_id` = '1' AND `P`.`is_gift_bag` = '0' AND `S`.`product_type` <> '20' AND `mer_status` = '1' AND `S`.`status` = '1' AND `P`.`is_select` = '1' order by  S.sort")
            products = cursor.fetchall()

            # 清空现有索引
            self.index.clear()
            self.products.clear()

            # 重新建立索引
            for product in products:
                self.add_product(product)
        finally:
            cursor.close()
            conn.close()

    def preprocess_text(self, text):
        """
        文本预处理函数
        参数:
            text: 输入的文本字符串
        返回:
            expanded_words: 处理后的词列表

        处理步骤:
        1. 将文本转换为小写
        2. 使用结巴分词进行分词
        3. 过滤停用词
        4. 扩展同义词
        """
        # 1. 转换为小写(针对英文)
        text = text.lower()

        # 2. 使用结巴分词
        words = jieba.lcut(text)

        # 3. 过滤停用词(如"的"、"了"、"在"等对文本分析无意义的词)
        words = [w for w in words if w not in Config.STOP_WORDS]

        # 4. 扩展同义词(比如"手机"="电话"="移动电话")
        expanded_words = []
        for word in words:
            # 如果该词在同义词典中存在
            if word in self.synonyms:
                # 将该词的所有同义词添加到结果中
                expanded_words.extend(self.synonyms[word])
            else:
                # 如果没有同义词,保留原词
                expanded_words.append(word)

        return expanded_words

    def preprocess_text1(self, text):
        """
        文本预处理优化版
        """
        # 1. 基础清理
        text = text.lower().strip()

        # 2. 特殊字符处理
        text = re.sub(r'[^\w\s]', ' ', text)

        # 3. 分词
        words = jieba.lcut(text)

        # 4. 停用词过滤
        words = [w for w in words if w not in Config.STOP_WORDS and len(w.strip()) > 1]

        # 5. 同义词扩展
        expanded_words = []
        for word in words:
            if word in self.synonyms:
                expanded_words.extend(self.synonyms[word])
            else:
                expanded_words.append(word)

        # 6. 词性过滤（可选）
        words_with_flags = pseg.cut(' '.join(expanded_words))
        filtered_words = [w.word for w in words_with_flags if w.flag in ['n', 'v', 'a']]

        return filtered_words

    def add_product(self, product):
        """
        添加商品到索引
        为商品名称中的每个词建立倒排索引
        """
        product_id = len(self.products)
        self.products.append(product)

        name = product['store_name']
        tokens = self.preprocess_text(name)

        # 为分词结果建立索引
        for token in tokens:
            self.index[token].append(product_id)

        # 为单字建立索引
        for char in name:
            if char not in Config.STOP_WORDS:
                self.index[char].append(product_id)
    def test(self,query):
        query_tokens = self.preprocess_text(query)
        return query_tokens

    def search_test(self, query, page=1, limit=4, top_k=100,zone_rule_id=2):
        """
        搜索商品
        使用TF-IDF算法计算相关性得分

        参数:
            query: 搜索查询字符串
            page: 当前页码(从1开始)
            limit: 每页显示数量
            top_k: 计算的最大结果数量

        返回:
            按相关性得分排序的商品列表和总数
        """
        query_tokens = self.preprocess_text(query)
        if not query_tokens:
            query_tokens = [query]

        scores = defaultdict(float)

        # 计算每个商品的得分
        for token in query_tokens:
            product_ids = self.index.get(token, [])
            if product_ids:
                # 计算IDF
                idf = np.log(len(self.products) / len(product_ids))
                for pid in product_ids:
                    # 对多字词给予更高的权重
                    weight = len(token) if len(token) > 1 else 0.5
                    scores[pid] += idf * weight

        # 排序并获取所有结果
        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        # 先根据条件过滤
        filtered_results = []
        if zone_rule_id:
            # 有 zone_rule_id 时进行过滤
            for pid, score in results:
                zone_rule_id_1 = self.products[pid].get('zone_rule_id')
                if zone_rule_id_1 is None:
                    zone_rule_id_1 = 0
                if int(zone_rule_id_1) == int(zone_rule_id):
                    filtered_results.append((pid, score))
        else:
            # 没有 zone_rule_id 时保留所有结果
            filtered_results = results
        # 对过滤后的结果进行分页
        start = (page - 1) * limit
        end = start + limit
        paginated_results = filtered_results[start:end]
        # 获取最终的spu_id列表
        products = []
        for pid, score in paginated_results:
            products.append(self.products[pid]['spu_id'])

        return products, len(filtered_results)



        # 构造返回数据
        # products = [
        #     {
        #
        #             'id': self.products[pid]['spu_id'],
        #             # 'name': self.products[pid]['store_name'],
        #             # 'price': float(self.products[pid]['price']),
        #             # 可以添加其他需要返回的字段
        #
        #         # 'score': score
        #     }
        #     for pid, score in paginated_results
        # ]

        # products = [
        #     self.products[pid]['spu_id']
        #     for pid, score in paginated_results
        # ]

        # return {
        #     # 'total': len(results),  # 总结果数
        #     'page': page,  # 当前页码
        #     # 'limit': limit,  # 每页数量
        #     # 'total_pages': math.ceil(len(results) / limit),  # 总页数
        #     'products': products #当前页的商品列表
        #
        # }

        # if zone_rule_id:
        #     # 有 zone_rule_id 时进行过滤
        #     products = [
        #         self.products[pid]['spu_id']
        #         for pid, score in paginated_results
        #
        #
        #         if self.products[pid].get('zone_rule_id') is not None and int(self.products[pid]['zone_rule_id']) == int(
        #             zone_rule_id)
        #
        #     ]
        # else:
        #     # 没有 zone_rule_id 时返回所有结果
        #     products = [
        #         self.products[pid]['spu_id']
        #         for pid, score in paginated_results
        #     ]

    def search(self, query, page=1, limit=4, top_k=100, zone_rule_id=2):
        """
        搜索商品
        使用TF-IDF算法计算相关性得分，并根据关键词权重调整排序

        参数:
            query: 搜索查询字符串
            page: 当前页码(从1开始)
            limit: 每页显示数量
            top_k: 计算的最大结果数量
            zone_rule_id: 区域规则ID

        返回:
            按相关性得分排序的商品列表和总数
        """
        # 关键词权重配置
        keyword_weights = {
            "油": {
                "食用油": 10,
                "大豆油": 9,
                "花生油": 9,
                "菜籽油": 8,
                "调和油": 8,
                "橄榄油": 7,
                "机油": 2,
                "润滑油": 2
            },
            "米": {
                "大米": 10,
                "小米": 9,
                "糯米": 8,
                "香米": 8,
                "稻米": 8,
                "米粉": 5,
                "米酒": 4
            },
            "面": {
                "面条": 10,
                "面粉": 9,
                "挂面": 8,
                "方便面": 8
            }
        }

        query_tokens = self.preprocess_text(query)
        if not query_tokens:
            query_tokens = [query]

        scores = defaultdict(float)

        # 计算每个商品的得分
        for token in query_tokens:
            product_ids = self.index.get(token, [])
            if product_ids:
                # 计算IDF
                idf = np.log(len(self.products) / len(product_ids))
                for pid in product_ids:
                    # 基础权重计算
                    weight = len(token) if len(token) > 1 else 0.5
                    base_score = idf * weight

                    # 应用关键词权重
                    product_name = self.products[pid].get('name', '').lower()
                    for keyword, weight_dict in keyword_weights.items():
                        if token == keyword:  # 如果搜索词匹配关键词
                            # 检查产品名称是否包含权重词
                            for term, weight_value in weight_dict.items():
                                if term in product_name:
                                    base_score *= weight_value
                                    break

                    scores[pid] += base_score

        # 排序并获取所有结果
        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # 根据zone_rule_id过滤
        filtered_results = []
        if zone_rule_id:
            for pid, score in results:
                zone_rule_id_1 = self.products[pid].get('zone_rule_id')
                if zone_rule_id_1 is None:
                    zone_rule_id_1 = 0
                if int(zone_rule_id_1) == int(zone_rule_id):
                    filtered_results.append((pid, score))
        else:
            filtered_results = results

        # 分页处理
        start = (page - 1) * limit
        end = start + limit
        paginated_results = filtered_results[start:end]

        # 获取最终的spu_id列表
        products = []
        for pid, score in paginated_results:
            products.append(self.products[pid]['spu_id'])

        return products, len(filtered_results)

    def refresh_index(self):
        """刷新索引"""
        self.load_products_from_db()

    def add_synonym(self, word, synonym):
        """
        添加新的同义词
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO synonyms (word, synonym) VALUES (%s, %s)",
                (word, synonym)
            )
            conn.commit()

            # 更新内存中的同义词词典
            if word in self.synonyms:
                self.synonyms[word].append(synonym)
            else:
                self.synonyms[word] = [synonym]

        finally:
            cursor.close()
            conn.close()

    def remove_synonym(self, word, synonym):
        """
        删除同义词
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM synonyms WHERE word = %s AND synonym = %s",
                (word, synonym)
            )
            conn.commit()

            # 更新内存中的同义词词典
            if word in self.synonyms and synonym in self.synonyms[word]:
                self.synonyms[word].remove(synonym)
                if not self.synonyms[word]:
                    del self.synonyms[word]

        finally:
            cursor.close()
            conn.close()

    def get_synonyms(self, word):
        """
        获取某个词的所有同义词
        """
        return self.synonyms.get(word, [])
