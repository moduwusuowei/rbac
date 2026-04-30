# -*- coding: utf-8 -*-
"""
组管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user_model import User, Group, Task
from app.core.logger import export_logger as logger

router = APIRouter()


# ==================== 组相关 API ====================


@router.get("/", response_model=List[dict])
async def get_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户所在的组列表"""
    logger.info(f"获取组列表 by {current_user.username}")
    
    groups = current_user.groups
    
    result = []
    for group in groups:
        # 检查是否是组长
        is_leader = group.leader_id == current_user.id if group.leader_id else False
        
        result.append({
            "id": group.id,
            "name": group.name,
            "code": group.code,
            "description": group.description,
            "is_active": group.is_active,
            "member_count": len(group.users),
            "is_leader": is_leader
        })
    
    return result


@router.post("/", response_model=dict)
async def create_group(
    group_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建组"""
    logger.info(f"创建组 by {current_user.username}")
    
    # 检查组名是否已存在
    existing_group = db.query(Group).filter(
        (Group.name == group_data["name"]) | (Group.code == group_data["code"])
    ).first()
    
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="组名或编码已存在"
        )
    
    # 创建组
    new_group = Group(
        name=group_data["name"],
        code=group_data["code"],
        description=group_data.get("description"),
        is_active=True,
        leader_id=current_user.id
    )
    
    # 添加创建者为第一个成员（组长）
    new_group.users.append(current_user)
    
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    logger.info(f"组创建成功: {new_group.name} by {current_user.username}")
    return {
        "id": new_group.id,
        "name": new_group.name,
        "message": "组创建成功"
    }


@router.get("/{group_id}", response_model=dict)
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取组详情"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组不存在"
        )
    
    # 检查用户是否在组内
    if current_user not in group.users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该组"
        )
    
    # 检查是否是组长
    is_leader = group.leader_id == current_user.id if group.leader_id else False
    
    # 获取组成员
    members = []
    for user in group.users:
        members.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_leader": user.id == group.leader_id if group.leader_id else False
        })
    
    # 获取组内任务数量
    task_count = db.query(Task).filter(
        Task.group_id == group_id,
        Task.is_active == True
    ).count()
    
    return {
        "id": group.id,
        "name": group.name,
        "code": group.code,
        "description": group.description,
        "is_active": group.is_active,
        "created_at": group.created_at,
        "updated_at": group.updated_at,
        "is_leader": is_leader,
        "member_count": len(members),
        "task_count": task_count,
        "members": members
    }


@router.put("/{group_id}", response_model=dict)
async def update_group(
    group_id: int,
    group_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新组信息"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组不存在"
        )
    
    # 检查是否是组长
    if not (group.leader_id == current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有组长可以更新组信息"
        )
    
    # 更新组信息
    for key, value in group_data.items():
        if hasattr(group, key):
            setattr(group, key, value)
    
    db.commit()
    db.refresh(group)
    
    logger.info(f"组更新成功: {group_id} by {current_user.username}")
    return {
        "id": group.id,
        "name": group.name,
        "message": "组信息更新成功"
    }


@router.post("/{group_id}/members", response_model=dict)
async def add_member(
    group_id: int,
    member_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加组成员"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组不存在"
        )
    
    # 检查是否是组长
    if not (group.leader_id == current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有组长可以添加成员"
        )
    
    # 查找用户
    username = member_data.get("username")
    user_id = member_data.get("user_id")
    
    # 判断 user_id 是否为数字
    if user_id:
        if isinstance(user_id, int) or (isinstance(user_id, str) and user_id.isdigit()):
            user = db.query(User).filter(User.id == int(user_id)).first()
        else:
            # 如果 user_id 不是数字，视为用户名
            user = db.query(User).filter(User.username == user_id).first()
    elif username:
        user = db.query(User).filter(User.username == username).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供用户名或用户ID"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户是否已在组内
    if user in group.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已在组内"
        )
    
    # 检查用户是否已经在其他组中
    if len(user.groups) > 0:
        other_group_names = [g.name for g in user.groups]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"用户已加入其他组: {', '.join(other_group_names)}，一个用户只能加入一个组"
        )
    
    # 添加用户到组
    group.users.append(user)
    db.commit()
    
    logger.info(f"添加组成员成功: {user.username} 到 {group.name} by {current_user.username}")
    return {
        "group_id": group_id,
        "user_id": user.id,
        "username": user.username,
        "message": "成员添加成功"
    }


@router.delete("/{group_id}/members/{user_id}", response_model=dict)
async def remove_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """移除组成员"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组不存在"
        )
    
    # 检查是否是组长
    if not (group.leader_id == current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有组长可以移除成员"
        )
    
    # 不能移除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能移除自己"
        )
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户是否在组内
    if user not in group.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户不在组内"
        )
    
    # 从组中移除用户
    group.users.remove(user)
    db.commit()
    
    logger.info(f"移除组成员成功: {user.username} 从 {group.name} by {current_user.username}")
    return {
        "group_id": group_id,
        "user_id": user_id,
        "message": "成员移除成功"
    }


@router.post("/{group_id}/transfer-leadership", response_model=dict)
async def transfer_leadership(
    group_id: int,
    leadership_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """交接组长权限"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组不存在"
        )
    
    # 检查是否是组长
    if not (group.leader_id == current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有组长可以交接权限"
        )
    
    # 查找新组长
    username = leadership_data.get("username")
    user_id = leadership_data.get("user_id")
    
    if user_id:
        new_leader = db.query(User).filter(User.id == user_id).first()
    elif username:
        new_leader = db.query(User).filter(User.username == username).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供用户名或用户ID"
        )
    
    if not new_leader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户是否在组内
    if new_leader not in group.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户不在组内"
        )
    
    # 不能交接给自己
    if new_leader.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能交接给自己"
        )
    
    # 更新组长
    group.leader_id = new_leader.id
    db.commit()
    
    logger.info(f"组长权限交接成功: {current_user.username} → {new_leader.username} in {group.name}")
    return {
        "group_id": group_id,
        "old_leader_id": current_user.id,
        "old_leader_name": current_user.username,
        "new_leader_id": new_leader.id,
        "new_leader_name": new_leader.username,
        "message": "组长权限交接成功"
    }
