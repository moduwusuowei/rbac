# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加组和任务相关表
"""
from sqlalchemy import create_engine, text
import os
import sys

# 获取当前文件所在目录的父目录作为项目根目录
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 使用固定的数据库连接字符串
DATABASE_URL = "sqlite:///rbac.db"

engine = create_engine(DATABASE_URL)

def migrate():
    """执行数据库迁移"""
    with engine.connect() as conn:
        print("开始数据库迁移...")
        
        # 1. 创建 groups 表
        print("\n1. 创建 groups 表...")
        try:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    code VARCHAR(50) NOT NULL UNIQUE,
                    description VARCHAR(200),
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            print("✓ groups 表创建成功")
        except Exception as e:
            print(f"✗ groups 表创建失败: {e}")
        
        # 2. 创建 user_groups 关联表
        print("\n2. 创建 user_groups 关联表...")
        try:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS user_groups (
                    user_id INTEGER NOT NULL,
                    group_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, group_id),
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
                )
            '''))
            print("✓ user_groups 表创建成功")
        except Exception as e:
            print(f"✗ user_groups 表创建失败: {e}")
        
        # 3. 创建 tasks 表
        print("\n3. 创建 tasks 表...")
        try:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(100) NOT NULL,
                    description VARCHAR(500),
                    status VARCHAR(20) DEFAULT 'pending',
                    priority VARCHAR(20) DEFAULT 'medium',
                    due_date DATETIME,
                    creator_id INTEGER NOT NULL,
                    group_id INTEGER,
                    assigned_to INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (creator_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
                    FOREIGN KEY (assigned_to) REFERENCES users (id) ON DELETE SET NULL
                )
            '''))
            print("✓ tasks 表创建成功")
        except Exception as e:
            print(f"✗ tasks 表创建失败: {e}")
        
        # 4. 提交事务
        conn.commit()
        print("\n数据库迁移完成！")

if __name__ == "__main__":
    migrate()
