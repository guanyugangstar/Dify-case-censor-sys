"""
日志工具模块
提供统一的日志记录功能，包含彩色日志格式化、日志管理器、装饰器和工具函数等功能
为审查系统提供企业级的日志管理解决方案
"""
import logging              # Python标准日志库
import logging.handlers     # 日志处理器扩展模块，提供轮转文件处理器等高级功能
import os                   # 操作系统接口，用于文件和目录操作
import sys                  # 系统特定参数和函数，用于访问标准输出等
from datetime import datetime  # 日期时间处理，用于记录函数执行时间
from typing import Optional    # 类型提示，表示可选参数


class ColoredFormatter(logging.Formatter):
    """
    彩色日志格式化器
    继承自logging.Formatter，为控制台输出添加ANSI颜色代码
    使不同级别的日志在终端中以不同颜色显示，提高可读性
    """
    
    # ANSI颜色代码字典，用于在终端显示彩色文本
    # 每个日志级别对应不同的颜色，便于快速识别日志重要性
    COLORS = {
        'DEBUG': '\033[36m',    # 青色 - 调试信息，开发时使用
        'INFO': '\033[32m',     # 绿色 - 一般信息，正常运行状态
        'WARNING': '\033[33m',  # 黄色 - 警告信息，需要注意但不影响运行
        'ERROR': '\033[31m',    # 红色 - 错误信息，程序出现问题
        'CRITICAL': '\033[35m', # 紫色 - 严重错误，可能导致程序崩溃
        'RESET': '\033[0m'      # 重置颜色到默认，避免颜色污染后续输出
    }
    
    def format(self, record):
        """
        重写format方法，为日志级别添加颜色
        
        Args:
            record: 日志记录对象，包含日志的所有信息
            
        Returns:
            str: 格式化后的带颜色的日志字符串
        """
        # 检查记录对象是否有levelname属性（日志级别名称）
        if hasattr(record, 'levelname'):
            # 获取对应级别的颜色代码，如果没有找到则使用重置色
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            # 为日志级别名称添加颜色包装：颜色代码 + 级别名 + 重置代码
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        # 调用父类的format方法完成最终的格式化
        return super().format(record)


class LoggerManager:
    """
    日志管理器
    采用单例模式管理整个应用的所有日志记录器
    负责日志系统的初始化配置和日志记录器的创建与缓存
    """
    
    _loggers = {}           # 类变量：存储所有已创建的日志记录器实例，避免重复创建
    _initialized = False    # 类变量：标记日志系统是否已经初始化，防止重复配置
    
    @classmethod
    def setup_logging(cls, config):
        """
        设置整个日志系统的配置
        这是日志系统的核心初始化方法，配置文件和控制台输出
        
        Args:
            config: 配置对象，包含日志相关的所有配置参数
                   - LOG_FILE: 日志文件路径
                   - LOG_LEVEL: 日志级别
                   - LOG_MAX_BYTES: 单个日志文件最大字节数
                   - LOG_BACKUP_COUNT: 保留的备份文件数量
        """
        # 防止重复初始化，确保日志系统只配置一次
        if cls._initialized:
            return
        
        # 确保日志目录存在，避免因目录不存在导致日志写入失败
        log_dir = os.path.dirname(config.LOG_FILE)  # 获取日志文件的目录路径
        if log_dir:  # 如果目录路径不为空
            os.makedirs(log_dir, exist_ok=True)     # 创建目录，exist_ok=True表示目录存在时不报错
        
        # 获取根日志记录器并设置全局日志级别
        root_logger = logging.getLogger()
        # 使用getattr动态获取日志级别常量，支持配置文件中的字符串配置
        root_logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
        
        # 清除现有的所有处理器，避免重复日志输出和配置冲突
        root_logger.handlers.clear()
        
        # 创建文件处理器 - 使用RotatingFileHandler实现日志文件轮转
        # 当日志文件达到指定大小时自动创建新文件，保持指定数量的备份
        file_handler = logging.handlers.RotatingFileHandler(
            config.LOG_FILE,                    # 日志文件路径
            maxBytes=config.LOG_MAX_BYTES,      # 单个日志文件最大字节数，超过后轮转
            backupCount=config.LOG_BACKUP_COUNT, # 保留的备份文件数量，旧文件会被删除
            encoding='utf-8'                    # 文件编码，支持中文字符
        )
        # 文件处理器使用与根日志记录器相同的级别
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
        
        # 创建控制台处理器 - 输出到标准输出（终端）
        console_handler = logging.StreamHandler(sys.stdout)
        # 控制台只显示INFO及以上级别的日志，避免调试信息过多
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式化器
        # 文件格式：包含完整信息（时间、名称、级别、文件名、行号、消息）
        # 便于问题追踪和调试
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'  # 完整的日期时间格式
        )
        
        # 控制台格式：使用彩色格式化器，信息相对简洁
        # 适合实时查看，不需要过多细节
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'  # 控制台只显示时分秒，节省空间
        )
        
        # 为处理器设置对应的格式化器
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # 将处理器添加到根日志记录器
        # 这样所有的日志记录器都会继承这些处理器
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # 标记为已初始化，防止重复配置
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取指定名称的日志记录器
        实现日志记录器的缓存机制，避免重复创建相同名称的记录器
        
        Args:
            name: 日志记录器的名称，通常使用模块名或功能名
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        # 如果该名称的日志记录器不存在，则创建并缓存
        if name not in cls._loggers:
            logger = logging.getLogger(name)  # 创建新的日志记录器
            cls._loggers[name] = logger       # 缓存到类变量中
        
        # 返回缓存的日志记录器实例
        return cls._loggers[name]


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器的便捷函数
    提供更简单的接口来获取日志记录器，支持自动推断调用模块名
    
    Args:
        name: 日志记录器名称，如果为None则自动使用调用模块名
              建议使用模块的完整路径作为名称，如 'censor_system.services.file_service'
        
    Returns:
        logging.Logger: 配置好的日志记录器实例
        
    Example:
        # 手动指定名称
        logger = get_logger('my_module')
        
        # 自动使用当前模块名
        logger = get_logger()
    """
    if name is None:
        # 使用Python的inspect模块获取调用者信息
        # 这样可以自动推断出调用get_logger的模块名
        import inspect
        frame = inspect.currentframe().f_back  # 获取调用者的栈帧
        # 从调用者的全局变量中获取模块名（__name__变量）
        name = frame.f_globals.get('__name__', 'unknown')
    
    # 委托给LoggerManager来实际创建和管理日志记录器
    return LoggerManager.get_logger(name)


def log_function_call(func):
    """
    函数调用日志装饰器
    自动记录函数的调用信息、执行时间和异常情况
    适用于需要监控性能和调试的重要函数
    
    功能特性：
    1. 记录函数调用时的参数信息
    2. 测量并记录函数执行时间
    3. 自动捕获和记录异常信息
    4. 不改变原函数的返回值和异常行为
    
    Args:
        func: 被装饰的函数对象
        
    Returns:
        function: 装饰后的函数，保持原函数的所有功能
        
    Example:
        @log_function_call
        def process_file(filename):
            # 处理文件的代码
            pass
            
        # 调用时会自动记录日志
        process_file('test.txt')
    """
    def wrapper(*args, **kwargs):
        # 获取函数所在模块的日志记录器
        # 使用func.__module__确保日志记录器名称与函数所在模块一致
        logger = get_logger(func.__module__)
        
        # 记录函数调用信息（DEBUG级别）
        # 包含函数名和传入的参数，便于调试和问题追踪
        logger.debug(f"调用函数 {func.__name__} - 参数: args={args}, kwargs={kwargs}")
        
        try:
            # 记录函数开始执行的时间
            start_time = datetime.now()
            
            # 执行原函数，保持所有原有的功能和行为
            result = func(*args, **kwargs)
            
            # 记录函数执行结束的时间
            end_time = datetime.now()
            
            # 计算函数执行耗时（秒）
            duration = (end_time - start_time).total_seconds()
            
            # 记录函数执行成功的信息，包含耗时统计
            logger.debug(f"函数 {func.__name__} 执行完成 - 耗时: {duration:.3f}秒")
            
            # 返回原函数的执行结果
            return result
            
        except Exception as e:
            # 捕获函数执行过程中的任何异常
            # 记录详细的错误信息，包含完整的异常堆栈
            logger.error(f"函数 {func.__name__} 执行失败 - 错误: {str(e)}", exc_info=True)
            
            # 重新抛出异常，不改变原有的异常处理流程
            # 这样调用者仍然可以正常处理异常
            raise
    
    # 返回包装后的函数
    return wrapper


def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """
    记录异常信息的工具函数
    提供统一的异常记录格式，便于问题追踪和分析
    
    Args:
        logger: 日志记录器实例，用于输出异常信息
        exception: 异常对象，包含异常的详细信息
        context: 上下文信息，用于提供异常发生时的额外背景信息
                例如："处理文件时"、"连接数据库时"等
    
    Features:
        - 自动提取异常类型和异常消息
        - 包含完整的异常堆栈信息（exc_info=True）
        - 支持上下文信息，便于定位问题发生的场景
        
    Example:
        try:
            # 一些可能出错的代码
            process_file(filename)
        except Exception as e:
            log_exception(logger, e, "处理文件时")
    """
    # 构建错误消息，包含异常类型名称和异常详细信息
    # 如果提供了上下文信息，则包含在错误消息中
    if context:
        error_msg = f"{context} - {type(exception).__name__}: {str(exception)}"
    else:
        error_msg = f"{type(exception).__name__}: {str(exception)}"
    
    # 记录错误日志，exc_info=True会自动包含完整的异常堆栈信息
    # 这对于调试和问题定位非常重要
    logger.error(error_msg, exc_info=True)


def log_request(logger: logging.Logger, request, response_status: int = None):
    """
    记录HTTP请求信息的工具函数
    专门用于Web应用的请求日志记录，便于监控和分析用户行为
    
    Args:
        logger: 日志记录器实例
        request: Flask请求对象，包含HTTP请求的所有信息
        response_status: HTTP响应状态码（可选），如200、404、500等
    
    记录的信息包括：
        - HTTP方法（GET、POST、PUT、DELETE等）
        - 完整的请求URL
        - 客户端IP地址
        - 用户代理字符串（浏览器信息）
        - 响应状态码（如果提供）
        
    Example:
        @app.route('/api/upload')
        def upload_file():
            try:
                # 处理上传逻辑
                result = process_upload(request)
                log_request(api_logger, request, 200)
                return result
            except Exception as e:
                log_request(api_logger, request, 500)
                raise
    """
    # 构建请求信息字典，包含关键的请求数据
    log_data = {
        'method': request.method,                           # HTTP方法
        'url': request.url,                                # 完整的请求URL
        'remote_addr': request.remote_addr,                # 客户端IP地址
        'user_agent': request.headers.get('User-Agent', ''), # 用户代理字符串
    }
    
    # 如果提供了响应状态码，则添加到日志数据中
    # 这有助于分析请求的处理结果
    if response_status:
        log_data['status'] = response_status
    
    # 使用INFO级别记录HTTP请求信息
    # INFO级别确保这些重要的访问信息会被记录
    logger.info(f"HTTP请求 - {log_data}")


# 预定义的日志记录器
# 为系统的不同模块预先创建专用的日志记录器，便于分类管理日志
# 使用统一的命名规范：censor_system.模块名

# 应用主模块日志记录器 - 记录应用启动、配置、主要流程等信息
app_logger = get_logger('censor_system.app')

# 文件处理模块日志记录器 - 记录文件上传、处理、存储等操作
file_logger = get_logger('censor_system.file')

# API接口模块日志记录器 - 记录API调用、请求响应等信息
api_logger = get_logger('censor_system.api')

# 验证模块日志记录器 - 记录数据验证、审查结果等信息
validation_logger = get_logger('censor_system.validation')