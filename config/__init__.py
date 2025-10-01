"""
配置模块
包含应用的所有配置和常量定义
"""

from .settings import Config, get_config
from .constants import *

__all__ = ['Config', 'get_config']