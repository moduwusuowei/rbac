# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 为users表添加头像相关字段
"""
from sqlalchemy import text
from app.core.database import engine


def migrate():
    """执行数据库迁移"""
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]

        # 添加 avatar_url 字段
        if 'avatar_url' not in columns:
            conn.execute(text('ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500)'))
            print("✓ 添加 avatar_url 字段成功")

        # 添加 avatar_path 字段
        if 'avatar_path' not in columns:
            conn.execute(text('ALTER TABLE users ADD COLUMN avatar_path VARCHAR(500)'))
            print("✓ 添加 avatar_path 字段成功")

        # 添加 avatar_id 字段
        if 'avatar_id' not in columns:
            conn.execute(text('ALTER TABLE users ADD COLUMN avatar_id VARCHAR(100)'))
            print("✓ 添加 avatar_id 字段成功")

        conn.commit()
        print("\n数据库迁移完成！")


if __name__ == "__main__":
    migrate()
