# -*- coding: utf-8 -*-
"""
角色管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user, check_role, check_permission
from app.models.user_model import User, Role, Permission

router = APIRouter()


class RoleCreate(BaseModel):
    """创建角色请求"""
    name: str
    code: str
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(BaseModel):
    """角色响应"""
    model_config = {"from_attributes": True}
    
    id: int
    name: str
    code: str
    description: Optional[str]
    is_active: bool
    permissions: List[str]


@router.get("", response_model=List[RoleResponse])
async def get_roles(
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("role:read")),
    db: Session = Depends(get_db)
):
    """获取角色列表"""
    # 非超级管理员只能看到自己拥有的角色
    if not current_user.is_superuser:
        # 创建角色响应列表，转换权限为字符串列表
        role_responses = []
        for role in current_user.roles:
            role_dict = {
                "id": role.id,
                "name": role.name,
                "code": role.code,
                "description": role.description,
                "is_active": role.is_active,
                "permissions": [p.code for p in role.permissions]
            }
            role_responses.append(role_dict)
        return role_responses
    
    roles = db.query(Role).all()
    # 创建角色响应列表，转换权限为字符串列表
    role_responses = []
    for role in roles:
        role_dict = {
            "id": role.id,
            "name": role.name,
            "code": role.code,
            "description": role.description,
            "is_active": role.is_active,
            "permissions": [p.code for p in role.permissions]
        }
        role_responses.append(role_dict)
    return role_responses


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("role:read")),
    db: Session = Depends(get_db)
):
    """获取单个角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 创建角色响应字典，转换权限为字符串列表
    role_dict = {
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "description": role.description,
        "is_active": role.is_active,
        "permissions": [p.code for p in role.permissions]
    }
    return role_dict


@router.post("", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("role:manage")),
    db: Session = Depends(get_db)
):
    """创建角色"""
    
    # 检查角色编码是否已存在
    existing = db.query(Role).filter(Role.code == role_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色编码已存在"
        )
    
    # 查找权限
    permissions = []
    if role_data.permission_ids:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_data.permission_ids)
        ).all()
    
    # 创建角色
    role = Role(
        name=role_data.name,
        code=role_data.code,
        description=role_data.description,
        permissions=permissions
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    
    # 创建角色响应字典，转换权限为字符串列表
    role_dict = {
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "description": role.description,
        "is_active": role.is_active,
        "permissions": [p.code for p in role.permissions]
    }
    return role_dict


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("role:manage")),
    db: Session = Depends(get_db)
):
    """更新角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 更新角色信息
    role.name = role_data.name
    role.description = role_data.description
    
    if role_data.permission_ids:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_data.permission_ids)
        ).all()
        role.permissions = permissions
    
    db.commit()
    db.refresh(role)
    
    # 创建角色响应字典，转换权限为字符串列表
    role_dict = {
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "description": role.description,
        "is_active": role.is_active,
        "permissions": [p.code for p in role.permissions]
    }
    return role_dict


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("role:manage")),
    db: Session = Depends(get_db)
):
    """删除角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 检查是否有关联用户
    if role.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该角色已被用户使用，无法删除"
        )
    
    db.delete(role)
    db.commit()
    
    return {"message": "角色删除成功"}