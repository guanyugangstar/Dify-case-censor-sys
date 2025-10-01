"""
验证服务模块
提供各种验证功能
"""
from typing import Tuple, Optional
from werkzeug.datastructures import FileStorage

from config.constants import (
    ALLOWED_EXTENSIONS, ERROR_MESSAGES, 
    CategoryEnum, ContractingPartyEnum, ReviewTypeEnum
)
from utils.exceptions import (
    FileValidationError, UnsupportedFileTypeError, 
    FileSizeExceededError, EmptyFileError,
    InvalidParameterError, MissingParameterError
)
from utils.logger import get_logger

logger = get_logger(__name__)


class ValidationService:
    """验证服务类"""
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """
        检查文件扩展名是否被允许
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否允许
        """
        return ('.' in filename and 
                filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)
    
    @staticmethod
    def validate_file(file: FileStorage, max_size: int) -> Tuple[bool, Optional[str]]:
        """
        全面的文件验证
        
        Args:
            file: 上传的文件对象
            max_size: 最大文件大小（字节）
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误消息)
        """
        try:
            # 检查文件是否存在
            if not file:
                raise FileValidationError(ERROR_MESSAGES['NO_FILE_SELECTED'])
            
            # 检查文件名
            if file.filename == '':
                raise EmptyFileError(ERROR_MESSAGES['EMPTY_FILENAME'])
            
            # 检查文件扩展名
            if not ValidationService.validate_file_extension(file.filename):
                formats = ', '.join(sorted(ALLOWED_EXTENSIONS))
                raise UnsupportedFileTypeError(
                    ERROR_MESSAGES['UNSUPPORTED_FILE_TYPE'].format(formats=formats)
                )
            
            # 检查文件大小
            file.seek(0, 2)  # 移动到文件末尾
            file_size = file.tell()
            file.seek(0)  # 重置到文件开头
            
            if file_size > max_size:
                max_size_mb = max_size // (1024 * 1024)
                raise FileSizeExceededError(
                    ERROR_MESSAGES['FILE_TOO_LARGE'].format(max_size=max_size_mb)
                )
            
            if file_size == 0:
                raise EmptyFileError(ERROR_MESSAGES['EMPTY_FILE'])
            
            logger.info(f"文件验证通过: {file.filename}, 大小: {file_size} bytes")
            return True, None
            
        except FileValidationError as e:
            logger.warning(f"文件验证失败: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"文件验证过程中发生未知错误: {str(e)}")
            return False, "文件验证失败"
    
    @staticmethod
    def validate_review_type(review_type: str) -> bool:
        """
        验证审查类型
        
        Args:
            review_type: 审查类型
            
        Returns:
            bool: 是否有效
        """
        try:
            return review_type in [e.value for e in ReviewTypeEnum]
        except Exception:
            return False
    
    @staticmethod
    def validate_contracting_party(contracting_party: str) -> bool:
        """
        验证合同方类型
        
        Args:
            contracting_party: 合同方类型
            
        Returns:
            bool: 是否有效
        """
        try:
            return contracting_party in [e.value for e in ContractingPartyEnum]
        except Exception:
            return False
    
    @staticmethod
    def validate_category(category: str) -> bool:
        """
        验证审查类别
        
        Args:
            category: 审查类别
            
        Returns:
            bool: 是否有效
        """
        try:
            return category in [e.value for e in CategoryEnum]
        except Exception:
            return False
    
    @staticmethod
    def validate_upload_request(review_type: str, contracting_party: str = None) -> None:
        """
        验证上传请求参数
        
        Args:
            review_type: 审查类型
            contracting_party: 合同方类型（可选）
            
        Raises:
            MissingParameterError: 缺失必要参数
            InvalidParameterError: 参数无效
        """
        # 检查审查类型
        if not review_type:
            raise MissingParameterError(ERROR_MESSAGES['NO_REVIEW_TYPE'])
        
        if not ValidationService.validate_review_type(review_type):
            raise InvalidParameterError(ERROR_MESSAGES['INVALID_REVIEW_TYPE'])
        
        # 合同审查特殊验证
        if review_type == ReviewTypeEnum.合同审查.value:
            if not contracting_party:
                raise MissingParameterError(ERROR_MESSAGES['NO_CONTRACTING_PARTY'])
            
            if not ValidationService.validate_contracting_party(contracting_party):
                raise InvalidParameterError(ERROR_MESSAGES['INVALID_CONTRACTING_PARTY'])
        
        logger.info(f"请求参数验证通过: review_type={review_type}, contracting_party={contracting_party}")
    
    @staticmethod
    def get_category_from_review_type(review_type: str) -> str:
        """
        根据审查类型获取类别
        
        Args:
            review_type: 审查类型
            
        Returns:
            str: 类别
        """
        if review_type == ReviewTypeEnum.文件审查.value:
            return CategoryEnum.政策.value
        elif review_type == ReviewTypeEnum.合同审查.value:
            return CategoryEnum.合同.value
        else:
            raise InvalidParameterError(f"未知的审查类型: {review_type}")
    
    @staticmethod
    def validate_stream_chat_request(inputs: dict, user_id: str) -> None:
        """
        验证流式聊天请求参数
        
        Args:
            inputs: 输入参数
            user_id: 用户ID
            
        Raises:
            MissingParameterError: 缺失必要参数
        """
        if not inputs:
            raise MissingParameterError("inputs参数缺失")
        
        if not user_id:
            raise MissingParameterError("user_id参数缺失")
        
        logger.info(f"流式聊天请求验证通过: user_id={user_id}")