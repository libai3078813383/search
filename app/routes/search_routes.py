import traceback

from flask import Blueprint, jsonify, request
from app.services.search_engine import ProductSearchEngine
from utils.database import get_db_connection
from utils.logger_handler import logger
search_bp = Blueprint('search', __name__)
search_engine = ProductSearchEngine()


@search_bp.route('/search', methods=['GET'])
@logger.api_logger('商品搜索接口')
def search_products():
    """
    商品搜索接口
    参数：
        q: 搜索关键词
        limit: 返回结果数量限制（可选，默认1000）
    返回：
        {
            "query": "搜索关键词",
            "total": 结果总数,
            "results": [...结果列表...]
        }
    """
    try:
        # 记录完整的请求信息
        request_info = {
            'args': dict(request.args),  # 所有GET参数
            'headers': dict(request.headers),  # 所有请求头
            'method': request.method,  # 请求方法
            'path': request.path,  # 请求路径
            'url': request.url,  # 完整URL
            'remote_addr': request.remote_addr,  # 客户端IP
            'user_agent': request.user_agent.string  # 用户代理
        }
        logger.log_info('搜索接口原始请求信息', request_info)
        # 参数处理
        try:
            limit = int(request.args.get('limit', 1000))
            query = request.args.get('query', '')
            page = int(request.args.get('page', 1))
            zone_rule_id = request.args.get('zone_rule_id', 0)
        except ValueError as ve:
            error_response = {
                'code': 400,
                'message': f'参数格式错误: {str(ve)}',
                'data': None
            }
            logger.log_error('搜索接口参数解析失败', {
                'request_info': request_info,
                'error': str(ve),
                'response': error_response
            })
            return error_response, 400
        # 参数验证
        if limit >= 1000:
            limit = 1000
            logger.log_info('搜索限制数量超过1000，已自动调整为1000', {
                'original_limit': request.args.get('limit'),
                'adjusted_limit': limit
            })
        if not query:
            error_response = {
                'code': 400,
                'message': '请提供搜索关键词',
                'data': None
            }
            logger.log_info('搜索接口参数验证失败', {
                'request_info': request_info,
                'response': error_response
            })
            return error_response, 400
        # 记录处理后的实际搜索参数
        search_params = {
            'query': query,
            'limit': limit,
            'page': page,
            'top_k': 1000
        }
        logger.log_info('搜索接口处理后的参数', search_params)
        # 执行搜索
        try:
            results,amount = search_engine.search(
                query=query,
                limit=limit,
                top_k=1000,
                page=page,
                zone_rule_id=zone_rule_id
            )
        except Exception as se:
            error_response = {
                'code': 500,
                'message': f'搜索引擎错误: {str(se)}',
                'data': None
            }
            logger.log_error('搜索引擎调用失败', {
                'request_info': request_info,
                'search_params': search_params,
                'error': str(se),
                'response': error_response
            })
            return error_response, 500
        # 构建响应
        response_data = {
            'code': 200,
            'message': 'success',
            'data': {
                'query': query,
                'amount': amount,
                'results': results
            }
        }
        # 记录成功响应
        logger.log_info('搜索接口调用成功', {
            'request_info': request_info,
            'search_params': search_params,
            'response': response_data
        })
        return response_data
    except Exception as e:
        # 记录未预期的错误
        error_response = {
            'code': 500,
            'message': f'搜索出错: {str(e)}',
            'data': None
        }

        logger.log_error('搜索接口发生未预期错误', {
            'request_info': request_info if 'request_info' in locals() else '请求信息获取失败',
            'search_params': search_params if 'search_params' in locals() else '搜索参数获取失败',
            'error': {
                'type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc()
            },
            'response': error_response
        })

        return error_response, 500


@search_bp.route('/add_product', methods=['POST'])
def add_product():
    """
    添加商品接口

    请求体：
    {
        "name": "商品名称",
        "price": 商品价格,
        "description": "商品描述"  // 可选
    }
    """
    try:
        data = request.get_json()

        if not data or 'name' not in data or 'price' not in data:
            return jsonify({
                'code': 400,
                'message': '请提供商品名称和价格',
                'data': None
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO products (name, price, description) VALUES (%s, %s, %s)",
                (data['name'], data['price'], data.get('description', ''))
            )
            conn.commit()

            # 重新加载商品数据
            search_engine.refresh_index()

            return jsonify({
                'code': 200,
                'message': '商品添加成功',
                'data': None
            })

        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'添加商品失败: {str(e)}',
            'data': None
        }), 500


@search_bp.route('/synonyms', methods=['GET', 'POST', 'DELETE'])
@logger.api_logger('获取同义词接口')
def manage_synonyms():
    """
    同义词管理接口

    GET: 获取同义词
    参数：
        word: 要查询的词

    POST: 添加同义词
    请求体：
    {
        "word": "原词",
        "synonyms": "同义词"
    }

    DELETE: 删除同义词
    请求体：
    {
        "word": "原词",
        "synonyms": "要删除的同义词"
    }
    """
    try:
        # 记录完整的请求信息
        request_info = {
            'args': dict(request.args),  # 所有GET参数
            'headers': dict(request.headers),  # 所有请求头
            'method': request.method,  # 请求方法
            'path': request.path,  # 请求路径
            'url': request.url,  # 完整URL
            'remote_addr': request.remote_addr,  # 客户端IP
            'user_agent': request.user_agent.string  # 用户代理
        }
        logger.log_info('获取同义词原始请求信息', request_info)
        if request.method == 'GET':
            word = request.args.get('word')

            if not word:
                return {
                    'code': 400,
                    'message': '请提供要查询的词',
                    'data': None
                }, 400

            synonyms = search_engine.get_synonyms(word)
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'word': word,
                    'synonyms': synonyms
                }
            })

        elif request.method == 'POST':
            data = request.get_json()
            if not data or 'word' not in data or 'synonyms' not in data:
                return {
                    'code': 400,
                    'message': '请提供原词和同义词',
                    'data': None
                }, 400

            word = data['word']
            new_synonym = data['synonyms']

            # 检查同义词是否已存在
            existing_synonyms = search_engine.get_synonyms(word)
            if new_synonym in existing_synonyms:
                return {
                    'code': 400,
                    'message': f'同义词 "{new_synonym}" 已存在',
                    'data': None
                }, 400

            search_engine.add_synonym(word, new_synonym)
            return {
                'code': 200,
                'message': '同义词添加成功',
                'data': None
            }

        elif request.method == 'DELETE':
            data = request.get_json()
            if not data or 'word' not in data or 'synonyms' not in data:
                return jsonify({
                    'code': 400,
                    'message': '请提供要删除的原词和同义词',
                    'data': None
                }), 400

            word = data['word']
            synonym_to_delete = data['synonyms']

            # 检查要删除的同义词是否存在
            existing_synonyms = search_engine.get_synonyms(word)
            if synonym_to_delete not in existing_synonyms:
                return {
                    'code': 400,
                    'message': f'同义词 "{synonym_to_delete}" 不存在',
                    'data': None
                }, 400

            search_engine.remove_synonym(word, synonym_to_delete)
            return {
                'code': 200,
                'message': '同义词删除成功',
                'data': None
            }

    except Exception as e:
        return {
            'code': 500,
            'message': f'操作失败: {str(e)}',
            'data': None
        }, 500


@search_bp.route('/refresh', methods=['POST'])

def refresh_index():
    """
    刷新搜索索引接口
    """
    try:
        search_engine.refresh_index()
        return jsonify({
            'code': 200,
            'message': '索引刷新成功',
            'data': None
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'刷新索引失败: {str(e)}',
            'data': None
        }), 500


# 错误处理
@search_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'code': 404,
        'message': '接口不存在',
        'data': None
    }), 404


@search_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'code': 500,
        'message': '服务器内部错误',
        'data': None
    }), 500
