# -*- coding: utf-8 -*-
"""
任务管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.auth import get_current_user, verify_password
from app.models.user_model import User, Task, Group
from app.core.logger import export_logger as logger

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_tasks(
    type: Optional[str] = Query(None, description="任务类型: personal, group, all"),
    group_id: Optional[int] = Query(None, description="组ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    try:
        logger.info(f"获取任务列表 by {current_user.username}")
        
        query = db.query(Task).filter(Task.is_active == True)
        
        if type == "personal":
            # 个人创建的任务
            query = query.filter(Task.creator_id == current_user.id)
        elif type == "group":
            # 组内任务
            if group_id:
                # 特定组的任务
                group = db.query(Group).filter(Group.id == group_id).first()
                if not group:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="组不存在"
                    )
                # 检查用户是否在该组
                if current_user not in group.users:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权访问该组任务"
                    )
                query = query.filter(Task.group_id == group_id)
            else:
                # 用户所在所有组的任务
                user_groups = [g.id for g in current_user.groups]
                query = query.filter(Task.group_id.in_(user_groups))
        
        tasks = query.all()
        
        # 构建响应，包含权限信息
        result = []
        for task in tasks:
            # 检查权限
            can_edit = False
            can_delete = False
            
            # 创建者可以编辑和删除
            if task.creator_id == current_user.id:
                can_edit = True
                can_delete = True
            else:
                # 检查是否是组长
                if task.group_id:
                    # 这里简化处理，实际应该有组长标识
                    # 假设第一个用户是组长
                    group = task.group
                    if group and group.users and group.users[0].id == current_user.id:
                        can_edit = True
                        can_delete = True
            
            result.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "start_date": task.start_date,
                "due_date": task.due_date,
                "creator_id": task.creator_id,
                "creator_name": task.creator.username if task.creator else "",
                "group_id": task.group_id,
                "group_name": task.group.name if task.group else "",
                "assigned_to": task.assigned_to,
                "assignee_name": task.assignee.username if task.assignee else "",
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "permissions": {
                    "can_edit": can_edit,
                    "can_delete": can_delete
                }
            })
        
        return result
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务列表失败: {str(e)}"
        )


@router.post("/", response_model=dict)
async def create_task(
    task_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建任务"""
    logger.info(f"创建任务 by {current_user.username}")
    
    # 验证组是否存在（如果指定了组）
    if task_data.get("group_id"):
        group = db.query(Group).filter(Group.id == task_data["group_id"]).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="组不存在"
            )
        # 检查用户是否在该组
        if current_user not in group.users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权在该组创建任务"
            )
    
    # 验证指派用户（如果指定了）
    if task_data.get("assigned_to"):
        assignee = db.query(User).filter(User.id == task_data["assigned_to"]).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指派用户不存在"
            )
    
    # 处理日期字段
    due_date = None
    if task_data.get("due_date"):
        due_date_str = task_data["due_date"]
        if isinstance(due_date_str, str):
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            except ValueError:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="日期格式无效"
                    )
        else:
            due_date = due_date_str
    
    # 处理开始日期字段
    start_date = None
    if task_data.get("start_date"):
        start_date_str = task_data["start_date"]
        if isinstance(start_date_str, str):
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="开始日期格式无效"
                    )
        else:
            start_date = start_date_str
    
    # 创建任务
    new_task = Task(
        title=task_data["title"],
        description=task_data.get("description"),
        status=task_data.get("status", "pending"),
        priority=task_data.get("priority", "medium"),
        start_date=start_date,
        due_date=due_date,
        creator_id=current_user.id,
        group_id=task_data.get("group_id"),
        assigned_to=task_data.get("assigned_to"),
        is_active=True
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    logger.info(f"任务创建成功: {new_task.id} by {current_user.username}")
    return {
        "id": new_task.id,
        "title": new_task.title,
        "message": "任务创建成功"
    }


@router.get("/{task_id}", response_model=dict)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    task = db.query(Task).filter(Task.id == task_id, Task.is_active == True).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查访问权限
    if task.creator_id != current_user.id:
        # 检查是否是组任务且用户在组内
        if task.group_id:
            group = task.group
            if not group or current_user not in group.users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问该任务"
                )
        else:
            # 个人任务，只有创建者可以访问
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问该任务"
            )
    
    # 检查编辑和删除权限
    can_edit = False
    can_delete = False
    
    if task.creator_id == current_user.id:
        can_edit = True
        can_delete = True
    else:
        # 检查是否是组长
        if task.group_id:
            group = task.group
            if group and group.users and group.users[0].id == current_user.id:
                can_edit = True
                can_delete = True
    
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "start_date": task.start_date,
        "due_date": task.due_date,
        "creator_id": task.creator_id,
        "creator_name": task.creator.username if task.creator else "",
        "group_id": task.group_id,
        "group_name": task.group.name if task.group else "",
        "assigned_to": task.assigned_to,
        "assignee_name": task.assignee.username if task.assignee else "",
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "permissions": {
            "can_edit": can_edit,
            "can_delete": can_delete
        }
    }


@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: int,
    task_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新任务"""
    logger.info(f"更新任务: {task_id} by {current_user.username}")
    
    task = db.query(Task).filter(Task.id == task_id, Task.is_active == True).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查编辑权限
    can_edit = False
    
    # 创建者可以编辑
    if task.creator_id == current_user.id:
        can_edit = True
    else:
        # 检查是否是组长
        if task.group_id:
            group = task.group
            if group and group.users and group.users[0].id == current_user.id:
                can_edit = True
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权编辑该任务"
        )
    
    # 处理日期字段
    if "due_date" in task_data and task_data["due_date"]:
        due_date_str = task_data["due_date"]
        if isinstance(due_date_str, str):
            try:
                task_data["due_date"] = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            except ValueError:
                try:
                    task_data["due_date"] = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="日期格式无效"
                    )
    
    # 处理开始日期字段
    if "start_date" in task_data and task_data["start_date"]:
        start_date_str = task_data["start_date"]
        if isinstance(start_date_str, str):
            try:
                task_data["start_date"] = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                try:
                    task_data["start_date"] = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="开始日期格式无效"
                    )
    
    # 更新任务
    for key, value in task_data.items():
        if hasattr(task, key):
            setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    
    logger.info(f"任务更新成功: {task_id} by {current_user.username}")
    return {
        "id": task.id,
        "title": task.title,
        "message": "任务更新成功"
    }


@router.delete("/{task_id}", response_model=dict)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除任务（软删除）"""
    logger.info(f"删除任务: {task_id} by {current_user.username}")
    
    task = db.query(Task).filter(Task.id == task_id, Task.is_active == True).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查删除权限
    can_delete = False
    
    # 创建者可以删除
    if task.creator_id == current_user.id:
        can_delete = True
    else:
        # 检查是否是组长
        if task.group_id:
            group = task.group
            if group and group.users and group.users[0].id == current_user.id:
                can_delete = True
    
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除该任务"
        )
    
    # 软删除
    task.is_active = False
    db.commit()
    
    logger.info(f"任务删除成功: {task_id} by {current_user.username}")
    return {
        "id": task.id,
        "message": "任务删除成功"
    }
