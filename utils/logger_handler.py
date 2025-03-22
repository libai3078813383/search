# # utils/logger_handler.py
#
# import os
# import logging
# from logging.handlers import TimedRotatingFileHandler
# import time
# from flask import request, g
# import json
# from functools import wraps
#
#
# class LoggerHandler:
#     """
#     日志处理器类
#     用于统一处理项目中的日志记录功能
#     包括访问日志、错误日志等
#     """
#
#     def __init__(self, app=None):
#         """
#         初始化日志处理器
#         :param app: Flask应用实例
#         """
#         self.app = app
#         if app:
#             self.init_app(app)
#
#     def init_app(self, app):
#         """
#         初始化日志配置
#         :param app: Flask应用实例
#         """
#         # 确保日志目录存在
#         log_path = app.config.get('LOG_PATH', 'logs')
#         if not os.path.exists(log_path):
#             os.makedirs(log_path)
#
#         # 配置访问日志
#         access_handler = TimedRotatingFileHandler(
#             os.path.join(log_path, 'access.log'),  # 日志文件路径
#             when='D',  # 按天切割日志
#             interval=1,  # 每1天切割一次
#             backupCount=30,  # 保留30天的日志
#             encoding='utf-8'  # 使用utf-8编码
#         )
#         # 设置访问日志格式
#         access_handler.setFormatter(logging.Formatter(
#             '%(asctime)s - %(levelname)s - %(message)s'
#         ))
#         self.access_logger = logging.getLogger('access_log')
#         self.access_logger.addHandler(access_handler)
#         self.access_logger.setLevel(logging.INFO)
#
#         # 配置错误日志
#         error_handler = TimedRotatingFileHandler(
#             os.path.join(log_path, 'error.log'),
#             when='D',
#             interval=1,
#             backupCount=30,
#             encoding='utf-8'
#         )
#         # 设置错误日志格式
#         error_handler.setFormatter(logging.Formatter(
#             '%(asctime)s - %(levelname)s - %(message)s\n'
#         ))
#         self.error_logger = logging.getLogger('error_log')
#         self.error_logger.addHandler(error_handler)
#         self.error_logger.setLevel(logging.ERROR)
#
#         # 注册Flask请求处理器
#         app.before_request(self.before_request)
#         app.after_request(self.after_request)
#         app.errorhandler(Exception)(self.handle_error)
#
#     def before_request(self):
#         """
#         请求前处理
#         记录请求开始时间
#         """
#         g.start_time = time.time()
#
#     def after_request(self, response):
#         """
#         请求后处理
#         记录访问日志
#         :param response: 响应对象
#         :return: 响应对象
#         """
#         # 不记录静态文件的访问日志
#         if not request.path.startswith('/static'):
#             # 计算请求处理时间
#             duration = time.time() - g.start_time
#
#             # 构建日志数据
#             log_data = {
#                 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
#                 'method': request.method,  # 请求方法
#                 'path': request.path,  # 请求路径
#                 'status': response.status_code,  # 响应状态码
#                 'duration': f'{duration:.3f}s',  # 处理时间
#                 'ip': request.remote_addr,  # 请求IP
#                 'user_agent': request.user_agent.string,  # 用户代理
#                 'args': dict(request.args),  # GET参数
#                 'form': dict(request.form),  # POST参数
#                 'json': request.get_json(silent=True)  # JSON数据
#             }
#
#             # 记录访问日志
#             self.access_logger.info(json.dumps(log_data))
#
#         return response
#
#     def handle_error(self, error):
#         """
#         统一错误处理
#         :param error: 错误对象
#         :return: 错误响应
#         """
#         self.error_logger.exception(f"Error occurred: {str(error)}")
#         return {'error': str(error)}, 500
#
#     def log_info(self, message, extra=None):
#         """
#         记录信息日志
#         :param message: 日志消息
#         :param extra: 额外信息
#         """
#         if extra:
#             message = f"{message} - {json.dumps(extra)}"
#         self.access_logger.info(message)
#
#     def log_error(self, message, error=None):
#         """
#         记录错误日志
#         :param message: 错误消息
#         :param error: 错误对象
#         """
#         if error:
#             self.error_logger.exception(f"{message}: {str(error)}")
#         else:
#             self.error_logger.error(message)
#
#     def api_logger(self, description=""):
#         """
#         API日志装饰器
#         用于记录API调用的详细信息
#         :param description: API描述
#         """
#
#         def decorator(f):
#             @wraps(f)
#             def decorated_function(*args, **kwargs):
#                 start_time = time.time()
#
#                 try:
#                     # 执行API处理函数
#                     result = f(*args, **kwargs)
#                     duration = time.time() - start_time
#
#                     # 构建日志数据
#                     log_data = {
#                         'api': description or f.__name__,
#                         'method': request.method,
#                         'path': request.path,
#                         'duration': f'{duration:.3f}s',
#                         'args': dict(request.args),
#                         'json': request.get_json(silent=True),
#                         'result': result
#                     }
#
#                     # 记录成功日志
#                     self.log_info(f"API Call Success: {f.__name__}", log_data)
#                     return result
#
#                 except Exception as e:
#                     # 记录失败日志
#                     self.log_error(f"API Call Failed: {f.__name__}", e)
#                     raise
#
#             return decorated_function
#
#         return decorator
#
#
# # 创建全局日志处理器实例
# logger = LoggerHandler()
