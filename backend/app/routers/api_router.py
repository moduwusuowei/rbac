# -*- coding: utf-8 -*-
"""
API 路由注册
"""
from fastapi import APIRouter
from app.api.v1 import auth, users, roles, permissions, products, phones, public, uploads, tasks, groups


api_router = APIRouter()

# 认证路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)

# 用户管理路由
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户管理"]
)

# 角色管理路由
api_router.include_router(
    roles.router,
    prefix="/roles",
    tags=["角色管理"]
)

# 权限管理路由
api_router.include_router(
    permissions.router,
    prefix="/permissions",
    tags=["权限管理"]
)

# 商品管理路由
api_router.include_router(
    products.router,
    prefix="/products",
    tags=["商品管理"]
)

# 手机管理路由
api_router.include_router(
    phones.router,
    prefix="/phones",
    tags=["手机管理"]
)

# 公共路由（无需权限）
api_router.include_router(
    public.router,
    prefix="/public",
    tags=["公共接口"]
)

# 文件上传路由
api_router.include_router(
    uploads.router,
    prefix="/uploads",
    tags=["文件上传"]
)

# 任务管理路由
api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["任务管理"]
)

# 组管理路由
api_router.include_router(
    groups.router,
    prefix="/groups",
    tags=["组管理"]
)
