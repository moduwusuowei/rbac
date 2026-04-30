# -*- coding: utf-8 -*-
"""
日志配置模块 - 使用loguru
"""
import os
from loguru import logger
from datetime import datetime

# 日志文件目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志文件路径
LOG_FILE = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# 配置logger
# 移除默认的控制台输出
logger.remove()

# 添加控制台输出
logger.add(
    sink=print,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True
)

# 添加文件输出
logger.add(
    sink=LOG_FILE,
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="00:00",  # 每天00:00创建新的日志文件
    retention="7 days",  # 保留7天的日志
    compression="zip"  # 压缩旧日志
)

# 测试日志
logger.info("Logger initialized successfully")

# 导出logger实例
export_logger = logger
