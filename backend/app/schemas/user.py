# -*- coding: utf-8 -*-
"""
用户相关的Schema
"""
from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: str
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """创建用户模型"""
    password: str
    role_ids: Optional[List[int]] = None


class UserUpdate(BaseModel):
    """更新用户模型"""
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role_ids: Optional[List[int]] = None


class UserResponse(BaseModel):
    """用户响应模型"""
    model_config = {"from_attributes": True}
    
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    roles: List[str]
