# -*- coding: utf-8 -*-
"""
测试用户注册功能
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.database import get_db
from app.models.user_model import User
from sqlalchemy.orm import Session
import uuid

client = TestClient(app)


# 测试注册成功
def test_register_success():
    """测试注册成功"""
    # 生成唯一的用户名和邮箱
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    password = "Password123!"
    
    # 发送注册请求
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password
        }
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "注册成功"
    assert data["username"] == username
    assert data["email"] == email
    assert "user_id" in data
    
    # 验证用户已创建
    from app.core.database import engine
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        assert user is not None
        assert user.email == email
        assert user.is_active == True
        assert user.is_superuser == False
    finally:
        db.close()


# 测试密码不匹配
def test_register_password_mismatch():
    """测试密码不匹配"""
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    
    # 发送注册请求，密码和确认密码不匹配
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password1234!"
        }
    )
    
    # 验证响应
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "密码和确认密码不匹配"


# 测试用户名已存在
def test_register_username_exists():
    """测试用户名已存在"""
    # 使用已知的用户名
    username = "admin"
    unique_id = str(uuid.uuid4())[:8]
    email = f"test_{unique_id}@example.com"
    
    # 发送注册请求
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }
    )
    
    # 验证响应
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "用户名已存在"


# 测试邮箱已存在
def test_register_email_exists():
    """测试邮箱已存在"""
    # 先创建一个用户
    unique_id1 = str(uuid.uuid4())[:8]
    username1 = f"testuser_{unique_id1}"
    email = f"test_{unique_id1}@example.com"
    
    # 第一次注册
    response1 = client.post(
        "/api/v1/auth/register",
        json={
            "username": username1,
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }
    )
    assert response1.status_code == 200
    
    # 第二次使用相同的邮箱注册
    unique_id2 = str(uuid.uuid4())[:8]
    username2 = f"testuser_{unique_id2}"
    
    response2 = client.post(
        "/api/v1/auth/register",
        json={
            "username": username2,
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }
    )
    
    # 验证响应
    assert response2.status_code == 400
    data = response2.json()
    assert data["detail"] == "邮箱已存在"


if __name__ == "__main__":
    # 运行测试
    print("测试注册成功...")
    test_register_success()
    print("✓ 注册成功测试通过")
    
    print("\n测试密码不匹配...")
    test_register_password_mismatch()
    print("✓ 密码不匹配测试通过")
    
    print("\n测试用户名已存在...")
    test_register_username_exists()
    print("✓ 用户名已存在测试通过")
    
    print("\n测试邮箱已存在...")
    test_register_email_exists()
    print("✓ 邮箱已存在测试通过")
    
    print("\n所有测试通过！")