def add_product_with_attrs(self, product):
    """添加带属性的商品"""
    product_id = len(self.products)
    self.products.append(product)

    # 索引商品名称
    name_tokens = self.preprocess_text(product['name'])

    # 索引商品属性
    attr_tokens = []
    for attr, value in product.get('attributes', {}).items():
        attr_tokens.extend(self.preprocess_text(f"{attr}{value}"))

    # 合并所有标记
    all_tokens = name_tokens + attr_tokens

    for token in all_tokens:
        self.index[token].append(product_id)


from pypinyin import lazy_pinyin


def preprocess_text(self, text):
    words = super().preprocess_text(text)

    # 添加拼音索引
    pinyin_words = []
    for word in words:
        pinyin = ''.join(lazy_pinyin(word))
        pinyin_words.append(pinyin)

    return words + pinyin_words


from fuzzywuzzy import fuzz


def search(self, query, top_k=10):
    # 基础搜索结果
    basic_results = super().search(query)

    # 对结果进行模糊匹配评分
    for result in basic_results:
        product_name = result['product']['name']
        fuzzy_score = fuzz.ratio(query, product_name)
        result['score'] *= (1 + fuzzy_score / 100)

    # 重新排序
    return sorted(basic_results, key=lambda x: x['score'], reverse=True)[:top_k]
