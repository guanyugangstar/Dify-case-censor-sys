"""
Dify API客户端模块
提供与Dify API的交互功能
"""
import json
import requests
from typing import Dict, Any, Iterator, Optional
from werkzeug.datastructures import FileStorage

from config.constants import API_TIMEOUT, CHUNK_SIZE
from utils.exceptions import DifyAPIError, FileUploadError
from utils.logger import get_logger

logger = get_logger(__name__)


class DifyClient:
    """Dify API客户端类"""
    
    def __init__(self, api_token: str, base_url: str):
        """
        初始化Dify客户端
        
        Args:
            api_token: API令牌
            base_url: API基础URL
        """
        self.api_token = api_token
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'User-Agent': 'CensorSystem/1.0'
        })
        
        logger.info(f"Dify客户端初始化完成: {base_url}")
    
    def upload_file(self, file: FileStorage, user_id: str = "default_user") -> str:
        """
        上传文件到Dify
        
        Args:
            file: 文件对象
            user_id: 用户ID
            
        Returns:
            str: 文件ID
            
        Raises:
            FileUploadError: 文件上传失败
        """
        try:
            url = f"{self.base_url}/files/upload"
            
            # 确保文件指针在开头
            file.seek(0)
            
            # 准备文件数据
            files = {
                'file': (file.filename, file.stream, file.mimetype or 'application/octet-stream')
            }
            
            data = {
                'user': user_id
            }
            
            logger.info(f"开始上传文件到Dify: {file.filename}")
            
            response = self.session.post(
                url,
                files=files,
                data=data,
                timeout=API_TIMEOUT
            )
            
            if response.status_code != 201:
                error_msg = f"文件上传失败: HTTP {response.status_code}"
                try:
                    error_detail = response.json().get('message', '')
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    pass
                
                logger.error(f"{error_msg}, 响应: {response.text}")
                raise FileUploadError(error_msg)
            
            result = response.json()
            file_id = result.get('id')
            
            if not file_id:
                raise FileUploadError("上传响应中缺少文件ID")
            
            logger.info(f"文件上传成功: {file.filename} -> {file_id}")
            return file_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"文件上传网络错误: {str(e)}")
            raise FileUploadError(f"网络错误: {str(e)}")
        except Exception as e:
            if isinstance(e, FileUploadError):
                raise
            logger.error(f"文件上传未知错误: {str(e)}")
            raise FileUploadError(f"上传失败: {str(e)}")
    
    def chat_stream(self, inputs: Dict[str, Any], user_id: str = "default_user") -> Iterator[str]:
        """
        流式聊天
        
        Args:
            inputs: 输入参数
            user_id: 用户ID
            
        Yields:
            str: 流式响应数据
            
        Raises:
            DifyAPIError: API调用失败
        """
        try:
            url = f"{self.base_url}/chat-messages"
            
            # 使用简单的查询，与原始程序保持一致
            query = "请审查"
            
            payload = {
                'inputs': inputs,
                'query': query,
                'response_mode': 'streaming',
                'conversation_id': '',
                'user': user_id
            }
            
            logger.info(f"开始流式聊天请求: {json.dumps(inputs, ensure_ascii=False)}")
            
            response = self.session.post(
                url,
                json=payload,
                stream=True,
                timeout=API_TIMEOUT
            )
            
            if response.status_code != 200:
                error_msg = f"聊天请求失败: HTTP {response.status_code}"
                try:
                    error_detail = response.json().get('message', '')
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    pass
                
                logger.error(f"{error_msg}, 响应: {response.text}")
                raise DifyAPIError(error_msg)
            
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    try:
                        if line.startswith(b'data:'):
                            content = line[5:].decode('utf-8').strip()
                            
                            # 跳过空内容
                            if not content:
                                continue
                                
                            logger.debug(f"接收到流式数据: {content}")
                            
                            # 尝试解析JSON来查看具体内容
                            try:
                                parsed_data = json.loads(content)
                                event_type = parsed_data.get('event', 'unknown')
                                logger.debug(f"事件类型: {event_type}")
                                
                                # 根据事件类型进行不同处理
                                if event_type == 'workflow_started':
                                    logger.info("工作流开始执行")
                                elif event_type == 'node_started':
                                    data = parsed_data.get('data', {})
                                    logger.info(f"节点开始: {data.get('title', 'Unknown')}")
                                elif event_type == 'node_finished':
                                    data = parsed_data.get('data', {})
                                    logger.info(f"节点完成: {data.get('title', 'Unknown')} - 状态: {data.get('status', 'unknown')}")
                                    if data.get('outputs'):
                                        logger.debug(f"节点输出: {data.get('outputs')}")
                                elif event_type == 'workflow_finished':
                                    data = parsed_data.get('data', {})
                                    logger.info(f"工作流完成 - 状态: {data.get('status', 'unknown')}")
                                elif event_type == 'message':
                                    logger.debug(f"消息块: {parsed_data.get('answer', '')}")
                                elif event_type == 'message_end':
                                    logger.info("消息结束")
                                elif event_type == 'error':
                                    logger.error(f"流式响应错误: {parsed_data.get('message', 'Unknown error')}")
                                    
                            except json.JSONDecodeError:
                                logger.debug(f"非JSON格式数据: {content}")
                            except Exception as e:
                                logger.warning(f"解析流式数据失败: {str(e)}")
                                
                            yield f"data: {content}\n\n"
                    except UnicodeDecodeError as e:
                        logger.warning(f"解码响应行失败: {str(e)}")
                        continue
            
            logger.info("流式聊天请求完成")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"聊天请求网络错误: {str(e)}")
            raise DifyAPIError(f"网络错误: {str(e)}")
        except Exception as e:
            if isinstance(e, DifyAPIError):
                raise
            logger.error(f"聊天请求未知错误: {str(e)}")
            raise DifyAPIError(f"聊天失败: {str(e)}")
    
    def chat_blocking(self, inputs: Dict[str, Any], user_id: str = "default_user") -> Dict[str, Any]:
        """
        阻塞式聊天
        
        Args:
            inputs: 输入参数
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 聊天响应
            
        Raises:
            DifyAPIError: API调用失败
        """
        try:
            url = f"{self.base_url}/chat-messages"
            
            # 使用简单的查询，与原始程序保持一致
            query = "请审查"
            
            payload = {
                'inputs': inputs,
                'query': query,
                'response_mode': 'blocking',
                'conversation_id': '',
                'user': user_id
            }
            
            logger.info(f"开始阻塞式聊天请求: {json.dumps(inputs, ensure_ascii=False)}")
            
            response = self.session.post(
                url,
                json=payload,
                timeout=API_TIMEOUT
            )
            
            if response.status_code != 200:
                error_msg = f"聊天请求失败: HTTP {response.status_code}"
                try:
                    error_detail = response.json().get('message', '')
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    pass
                
                logger.error(f"{error_msg}, 响应: {response.text}")
                raise DifyAPIError(error_msg)
            
            result = response.json()
            logger.info("阻塞式聊天请求完成")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"聊天请求网络错误: {str(e)}")
            raise DifyAPIError(f"网络错误: {str(e)}")
        except Exception as e:
            if isinstance(e, DifyAPIError):
                raise
            logger.error(f"聊天请求未知错误: {str(e)}")
            raise DifyAPIError(f"聊天失败: {str(e)}")
    
    def get_conversation_messages(self, conversation_id: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        获取对话消息
        
        Args:
            conversation_id: 对话ID
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 对话消息
            
        Raises:
            DifyAPIError: API调用失败
        """
        try:
            url = f"{self.base_url}/messages"
            
            params = {
                'conversation_id': conversation_id,
                'user': user_id
            }
            
            logger.info(f"获取对话消息: {conversation_id}")
            
            response = self.session.get(
                url,
                params=params,
                timeout=API_TIMEOUT
            )
            
            if response.status_code != 200:
                error_msg = f"获取对话消息失败: HTTP {response.status_code}"
                try:
                    error_detail = response.json().get('message', '')
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    pass
                
                logger.error(f"{error_msg}, 响应: {response.text}")
                raise DifyAPIError(error_msg)
            
            result = response.json()
            logger.info(f"获取对话消息成功: {conversation_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取对话消息网络错误: {str(e)}")
            raise DifyAPIError(f"网络错误: {str(e)}")
        except Exception as e:
            if isinstance(e, DifyAPIError):
                raise
            logger.error(f"获取对话消息未知错误: {str(e)}")
            raise DifyAPIError(f"获取对话消息失败: {str(e)}")
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 是否健康
        """
        try:
            # 尝试访问API根路径或健康检查端点
            url = f"{self.base_url}/"
            
            response = self.session.get(url, timeout=5)
            
            # 根据状态码判断健康状态
            is_healthy = response.status_code < 500
            
            if is_healthy:
                logger.debug("Dify API健康检查通过")
            else:
                logger.warning(f"Dify API健康检查失败: HTTP {response.status_code}")
            
            return is_healthy
            
        except Exception as e:
            logger.warning(f"Dify API健康检查异常: {str(e)}")
            return False
    
    def close(self):
        """关闭客户端连接"""
        try:
            self.session.close()
            logger.debug("Dify客户端连接已关闭")
        except Exception as e:
            logger.warning(f"关闭Dify客户端连接失败: {str(e)}")