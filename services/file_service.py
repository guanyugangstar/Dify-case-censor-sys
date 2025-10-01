"""
文件处理服务模块
提供文件上传、类型检测等功能
"""
import os
import secrets
import codecs
from typing import Dict, Any, Tuple
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from config.constants import EXT_TYPE_MAP, EXT_FILETYPE_MAP, SUPPORTED_FILE_TYPES
from utils.exceptions import FileUploadError, UnsupportedFileTypeError
from utils.logger import get_logger

logger = get_logger(__name__)


class FileService:
    """文件处理服务类"""
    
    @staticmethod
    def guess_file_type(file: FileStorage) -> str:
        """
        推测文件类型
        
        Args:
            file: 文件对象
            
        Returns:
            str: 文件类型 (document, image, audio, video, custom)
        """
        try:
            # 首先尝试从MIME类型推测
            mime = getattr(file, 'mimetype', None)
            ext = EXT_TYPE_MAP.get(mime)
            
            # 如果MIME类型推测失败，从文件扩展名推测
            if not ext and '.' in file.filename:
                ext = file.filename.rsplit('.', 1)[-1].lower()
            
            file_type = EXT_FILETYPE_MAP.get(ext, 'custom')
            
            logger.debug(f"文件类型推测: {file.filename} -> {file_type} (ext: {ext}, mime: {mime})")
            return file_type
            
        except Exception as e:
            logger.warning(f"文件类型推测失败: {str(e)}")
            return 'custom'
    
    @staticmethod
    def create_dify_file_input(file: FileStorage, file_id: str) -> Dict[str, Any]:
        """
        创建Dify API所需的文件输入格式
        
        Args:
            file: 文件对象
            file_id: 文件ID
            
        Returns:
            Dict[str, Any]: Dify文件输入格式
        """
        file_type = FileService.guess_file_type(file)
        
        return {
            'type': file_type,
            'upload_file_id': file_id,
            'transfer_method': 'local_file'
        }
    
    @staticmethod
    def validate_file_type_support(file_type: str) -> bool:
        """
        验证文件类型是否被支持
        
        Args:
            file_type: 文件类型
            
        Returns:
            bool: 是否支持
        """
        return file_type in SUPPORTED_FILE_TYPES
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """
        生成安全的文件名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            str: 安全的文件名
        """
        try:
            secure_name = secure_filename(original_filename)
            if not secure_name:
                # 如果secure_filename返回空字符串，生成一个随机文件名
                ext = ''
                if '.' in original_filename:
                    ext = '.' + original_filename.rsplit('.', 1)[-1].lower()
                secure_name = f"upload_{secrets.token_hex(8)}{ext}"
            
            logger.debug(f"生成安全文件名: {original_filename} -> {secure_name}")
            return secure_name
            
        except Exception as e:
            logger.warning(f"生成安全文件名失败: {str(e)}")
            return f"upload_{secrets.token_hex(8)}.tmp"
    
    @staticmethod
    def save_temp_file(file: FileStorage, upload_folder: str) -> str:
        """
        保存临时文件
        
        Args:
            file: 文件对象
            upload_folder: 上传目录
            
        Returns:
            str: 临时文件路径
            
        Raises:
            FileUploadError: 文件保存失败
        """
        try:
            # 确保上传目录存在
            os.makedirs(upload_folder, exist_ok=True)
            
            # 生成安全的文件名
            secure_name = FileService.generate_secure_filename(file.filename)
            temp_path = os.path.join(upload_folder, secure_name)
            
            # 保存文件
            file.save(temp_path)
            
            logger.info(f"临时文件保存成功: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"保存临时文件失败: {str(e)}")
            raise FileUploadError(f"文件保存失败: {str(e)}")
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """
        清理临时文件
        
        Args:
            file_path: 文件路径
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"临时文件清理成功: {file_path}")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {file_path}, 错误: {str(e)}")
    
    @staticmethod
    def decode_unicode_dict(data: Any) -> Any:
        """
        递归解码Unicode字典
        
        Args:
            data: 要解码的数据
            
        Returns:
            Any: 解码后的数据
        """
        try:
            if isinstance(data, dict):
                return {k: FileService.decode_unicode_dict(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [FileService.decode_unicode_dict(i) for i in data]
            elif isinstance(data, str):
                try:
                    return codecs.decode(data, 'unicode_escape')
                except Exception:
                    return data
            else:
                return data
        except Exception as e:
            logger.warning(f"Unicode解码失败: {str(e)}")
            return data
    
    @staticmethod
    def filter_none_values(obj: Any) -> Any:
        """
        过滤None值
        
        Args:
            obj: 要过滤的对象
            
        Returns:
            Any: 过滤后的对象
        """
        try:
            if isinstance(obj, dict):
                return {k: FileService.filter_none_values(v) 
                       for k, v in obj.items() if v is not None}
            elif isinstance(obj, list):
                return [FileService.filter_none_values(i) 
                       for i in obj if i is not None]
            else:
                return obj
        except Exception as e:
            logger.warning(f"过滤None值失败: {str(e)}")
            return obj
    
    @staticmethod
    def get_file_info(file: FileStorage) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file: 文件对象
            
        Returns:
            Dict[str, Any]: 文件信息
        """
        try:
            # 保存当前文件指针位置
            current_position = file.tell()
            
            # 获取文件大小
            file.seek(0, 2)
            file_size = file.tell()
            
            # 恢复文件指针到原始位置
            file.seek(current_position)
            
            return {
                'filename': file.filename,
                'size': file_size,
                'mimetype': getattr(file, 'mimetype', None),
                'type': FileService.guess_file_type(file)
            }
        except Exception as e:
            logger.error(f"获取文件信息失败: {str(e)}")
            # 确保在异常情况下也重置文件指针
            try:
                file.seek(0)
            except:
                pass
            return {
                'filename': getattr(file, 'filename', 'unknown'),
                'size': 0,
                'mimetype': None,
                'type': 'unknown'
            }