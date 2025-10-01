"""
自定义异常模块
定义应用中使用的所有自定义异常类
"""


class CensorSystemException(Exception):
    """审查系统基础异常类"""
    
    def __init__(self, message, error_code=None, details=None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class FileValidationError(CensorSystemException):
    """文件验证异常"""
    pass


class FileUploadError(CensorSystemException):
    """文件上传异常"""
    pass


class APIClientError(CensorSystemException):
    """API客户端异常"""
    pass


class ConfigurationError(CensorSystemException):
    """配置错误异常"""
    pass


class ValidationError(CensorSystemException):
    """验证错误异常"""
    pass


class ServiceError(CensorSystemException):
    """服务错误异常"""
    pass


# 具体的异常类型
class UnsupportedFileTypeError(FileValidationError):
    """不支持的文件类型异常"""
    pass


class FileSizeExceededError(FileValidationError):
    """文件大小超限异常"""
    pass


class EmptyFileError(FileValidationError):
    """空文件异常"""
    pass


class DifyAPIError(APIClientError):
    """Dify API异常"""
    pass


class NetworkError(APIClientError):
    """网络错误异常"""
    pass


class TimeoutError(APIClientError):
    """超时异常"""
    pass


class InvalidParameterError(ValidationError):
    """无效参数异常"""
    pass


class MissingParameterError(ValidationError):
    """缺失参数异常"""
    pass