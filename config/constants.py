"""
常量定义模块
定义应用中使用的所有常量
"""
import enum

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'txt', 'md', 'markdown', 'html',
    'xls', 'xlsx', 'ppt', 'pptx', 'xml', 'epub', 'csv',
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',
    'mp3', 'm4a', 'wav', 'webm', 'amr', 'mpga',
    'mp4', 'mov', 'mpeg'
}

# 文件类型映射
EXT_TYPE_MAP = {
    'application/pdf': 'pdf',
    'application/msword': 'doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'text/plain': 'txt',
    'text/markdown': 'markdown',
    'text/html': 'html',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.ms-powerpoint': 'ppt',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
    'application/xml': 'xml',
    'application/epub+zip': 'epub',
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/gif': 'gif',
    'image/webp': 'webp',
    'image/svg+xml': 'svg',
    'audio/mpeg': 'mp3',
    'audio/mp4': 'm4a',
    'audio/wav': 'wav',
    'audio/webm': 'webm',
    'audio/amr': 'amr',
    'video/mp4': 'mp4',
    'video/quicktime': 'mov',
    'video/mpeg': 'mpeg',
    'audio/mpga': 'mpga',
}

# 扩展名到文件类型映射
EXT_FILETYPE_MAP = {
    'pdf': 'document', 'doc': 'document', 'docx': 'document', 
    'txt': 'document', 'md': 'document', 'markdown': 'document', 'html': 'document',
    'xls': 'document', 'xlsx': 'document', 'ppt': 'document', 'pptx': 'document', 
    'xml': 'document', 'epub': 'document', 'csv': 'document', 'eml': 'document', 'msg': 'document',
    'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'webp': 'image', 'svg': 'image',
    'mp3': 'audio', 'm4a': 'audio', 'wav': 'audio', 'webm': 'audio', 'amr': 'audio', 'mpga': 'audio',
    'mp4': 'video', 'mov': 'video', 'mpeg': 'video',
}

# 支持的文件类型
SUPPORTED_FILE_TYPES = {'document', 'image', 'audio', 'video'}

# 默认配置值
DEFAULT_MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
DEFAULT_PORT = 5050
DEFAULT_HOST = '127.0.0.1'
DEFAULT_UPLOAD_FOLDER = 'static'
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_LOG_FILE = 'logs/app.log'

# API相关常量
API_TIMEOUT = 300  # 5分钟超时
CHUNK_SIZE = 8192  # 文件读取块大小

# 枚举类型定义
class CategoryEnum(str, enum.Enum):
    """审查类别枚举"""
    合同 = "合同"
    政策 = "政策"


class ContractingPartyEnum(str, enum.Enum):
    """合同方枚举"""
    甲方 = "甲方"
    乙方 = "乙方"
    丙方 = "丙方"


class ReviewTypeEnum(str, enum.Enum):
    """审查类型枚举"""
    合同审查 = "合同审查"
    文件审查 = "文件审查"


# 错误消息常量
ERROR_MESSAGES = {
    'NO_FILE_SELECTED': '未选择文件',
    'EMPTY_FILENAME': '文件名不能为空',
    'UNSUPPORTED_FILE_TYPE': '不支持的文件类型。支持的格式：{formats}',
    'FILE_TOO_LARGE': '文件过大，最大支持 {max_size}MB',
    'EMPTY_FILE': '文件不能为空',
    'NO_REVIEW_TYPE': '请选择审查类型',
    'NO_CONTRACTING_PARTY': '合同审查时需选择甲方、乙方或丙方',
    'INVALID_CONTRACTING_PARTY': '合同方类型不合法',
    'INVALID_REVIEW_TYPE': '审查类型不合法',
    'FILE_UPLOAD_FAILED': '文件上传失败: {error}',
    'UNSUPPORTED_FILE_FORMAT': '文件类型不被支持，请上传文档、图片、音频或视频类型文件',
    'MISSING_PARAMETERS': '参数缺失',
    'REQUEST_ERROR': '请求格式错误，请检查上传的文件和参数',
    'SERVER_ERROR': '服务器内部错误，请稍后重试',
    'MISSING_DIFY_TOKEN': 'DIFY_API_TOKEN环境变量未设置，请设置后重新启动应用'
}