# -*- coding: utf-8 -*-
"""
权限管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user, check_permission
from app.models.user_model import User, Permission
from app.core.logger import export_logger as logger

router = APIRouter()


class PermissionCreate(BaseModel):
    """创建权限请求"""
    name: str
    code: str
    description: Optional[str] = None


class PermissionResponse(BaseModel):
    """权限响应"""
    model_config = {"from_attributes": True}
    
    id: int
    name: str
    code: str
    description: Optional[str]


@router.get("", response_model=List[PermissionResponse])
async def get_permissions(
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("permission:read")),
    db: Session = Depends(get_db)
):
    """获取权限列表"""
    logger.info(f"获取权限列表 by {current_user.username}")
    permissions = db.query(Permission).all()
    logger.info(f"获取到 {len(permissions)} 个权限")
    return permissions


@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("permission:read")),
    db: Session = Depends(get_db)
):
    """获取单个权限"""
    logger.info(f"获取权限信息: {permission_id} by {current_user.username}")
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        logger.warning(f"获取权限失败 - 权限不存在: {permission_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    
    logger.info(f"获取权限成功: {permission.code}")
    return permission


@router.post("", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("permission:manage")),
    db: Session = Depends(get_db)
):
    """创建权限"""
    logger.info(f"创建权限请求: {permission_data.code} by {current_user.username}")
    
    # 检查权限编码是否已存在
    existing = db.query(Permission).filter(Permission.code == permission_data.code).first()
    if existing:
        logger.warning(f"创建权限失败 - 权限编码已存在: {permission_data.code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="权限编码已存在"
        )
    
    # 创建权限
    permission = Permission(
        name=permission_data.name,
        code=permission_data.code,
        description=permission_data.description
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    
    logger.info(f"权限创建成功: {permission.code}")
    return permission


@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    permission_data: PermissionCreate,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("permission:manage")),
    db: Session = Depends(get_db)
):
    """更新权限"""
    logger.info(f"更新权限请求: {permission_id} by {current_user.username}")
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        logger.warning(f"更新权限失败 - 权限不存在: {permission_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    
    # 检查权限编码是否已存在（排除当前权限）
    existing = db.query(Permission).filter(
        Permission.code == permission_data.code,
        Permission.id != permission_id
    ).first()
    if existing:
        logger.warning(f"更新权限失败 - 权限编码已存在: {permission_data.code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="权限编码已存在"
        )
    
    # 更新权限信息
    permission.name = permission_data.name
    permission.code = permission_data.code
    permission.description = permission_data.description
    
    db.commit()
    db.refresh(permission)
    
    logger.info(f"权限更新成功: {permission.code}")
    return permission


@router.delete("/{permission_id}")
async def delete_permission(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("permission:manage")),
    db: Session = Depends(get_db)
):
    """删除权限"""
    logger.info(f"删除权限请求: {permission_id} by {current_user.username}")
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        logger.warning(f"删除权限失败 - 权限不存在: {permission_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    
    # 检查是否有关联角色
    if permission.roles:
        logger.warning(f"删除权限失败 - 权限已被角色使用: {permission.code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该权限已被角色使用，无法删除"
        )
    
    db.delete(permission)
    db.commit()
    
    logger.info(f"权限删除成功: {permission.code}")
    return {"message": "权限删除成功"}
