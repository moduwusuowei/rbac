# -*- coding: utf-8 -*-
"""
用户管理 API 路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user, check_permission
from app.models.user_model import User, Role
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.logger import export_logger as logger

router = APIRouter()


@router.get("", response_model=List[UserResponse])
async def get_users(
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("user:read")),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    logger.info(f"获取用户列表 by {current_user.username}")
    users = db.query(User).all()
    logger.info(f"获取到 {len(users)} 个用户")
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            roles=[role.code for role in user.roles]
        )
        for user in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("user:read")),
    db: Session = Depends(get_db)
):
    """获取单个用户"""
    logger.info(f"获取用户信息: {user_id} by {current_user.username}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"获取用户失败 - 用户不存在: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    logger.info(f"获取用户成功: {user.username}")
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        roles=[role.code for role in user.roles]
    )


@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("user:create")),
    db: Session = Depends(get_db)
):
    """创建用户"""
    logger.info(f"创建用户请求: {user_data.username} by {current_user.username}")
    
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        logger.warning(f"创建用户失败 - 用户名已存在: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 查找角色
    roles = []
    if user_data.role_ids:
        roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
    
    # 创建用户
    from app.core.auth import get_password_hash
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email,
        roles=roles
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"用户创建成功: {user.username}")
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        roles=[role.code for role in user.roles]
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("user:update")),
    db: Session = Depends(get_db)
):
    """更新用户"""
    logger.info(f"更新用户请求: {user_id} by {current_user.username}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"更新用户失败 - 用户不存在: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新用户信息
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.password is not None:
        from app.core.auth import get_password_hash
        user.password_hash = get_password_hash(user_data.password)
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.is_superuser is not None:
        user.is_superuser = user_data.is_superuser
    if user_data.role_ids is not None:
        roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
        user.roles = roles
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"用户更新成功: {user.username}")
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        roles=[role.code for role in user.roles]
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("user:delete")),
    db: Session = Depends(get_db)
):
    """删除用户"""
    logger.info(f"删除用户请求: {user_id} by {current_user.username}")
    
    if user_id == current_user.id:
        logger.warning(f"删除用户失败 - 不能删除当前登录用户: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录用户"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"删除用户失败 - 用户不存在: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    username = user.username
    db.delete(user)
    db.commit()
    
    logger.info(f"用户删除成功: {username}")
    return {"message": "用户删除成功"}
