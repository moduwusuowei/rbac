# -*- coding: utf-8 -*-
"""
认证相关 schemas
"""
from pydantic import BaseModel
from typing import Optional, List


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user_info: dict


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str
    password: str
    email: Optional[str] = None
    role_ids: Optional[List[int]] = None


class UserResponse(BaseModel):
    """用户响应"""
    model_config = {"from_attributes": True}
    
    id: int
    username: str
    email: Optional[str]
    is_active: bool
    is_superuser: bool
    roles: List[str]


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    email: str
    password: str
    confirm_password: str


class RegisterResponse(BaseModel):
    """注册响应"""
    message: str
    user_id: int
    username: str
    email: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    current_password: str
    new_password: str
    confirm_password: str


class ChangePasswordResponse(BaseModel):
    """修改密码响应"""
    message: str
    success: bool