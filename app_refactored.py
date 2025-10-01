"""
审查系统主应用入口
简化的Flask应用启动文件
"""
from flask import Flask

from config import get_config
from routes import main_bp
from utils import get_logger


def create_app():
    """
    应用工厂函数
    创建并配置Flask应用实例
    
    Returns:
        Flask: 配置好的Flask应用实例
    """
    # 创建Flask应用
    app = Flask(__name__)
    
    # 加载配置
    config = get_config()
    app.config.from_object(config)
    
    # 设置日志
    logger = get_logger(__name__)
    logger.info("正在初始化审查系统应用...")
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    logger.info("路由蓝图注册完成")
    
    # 确保必要目录存在
    config.ensure_directories()
    logger.info("目录结构检查完成")
    
    # 验证配置
    try:
        config.validate()
        logger.info("配置验证通过")
    except Exception as e:
        logger.error(f"配置验证失败: {str(e)}")
        raise
    
    logger.info("审查系统应用初始化完成")
    return app


def main():
    """主函数"""
    try:
        # 创建应用
        app = create_app()
        
        # 获取配置
        config = get_config()
        
        # 启动应用
        logger = get_logger(__name__)
        logger.info(f"启动审查系统服务器: {config.HOST}:{config.PORT}")
        
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG
        )
        
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"应用启动失败: {str(e)}")
        raise


if __name__ == '__main__':
    main()