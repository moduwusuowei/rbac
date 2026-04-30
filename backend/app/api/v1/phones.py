# -*- coding: utf-8 -*-
"""
手机管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user, check_permission
from app.models.user_model import User, Phone
from app.core.logger import export_logger as logger

router = APIRouter()


class PhoneCreate(BaseModel):
    """创建手机请求"""
    name: str
    brand: str
    model: str
    price: float
    stock: int
    description: Optional[str] = None
    is_active: bool = True


class PhoneUpdate(BaseModel):
    """更新手机请求"""
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PhoneResponse(BaseModel):
    """手机响应"""
    model_config = {"from_attributes": True}
    
    id: int
    name: str
    brand: str
    model: str
    price: float
    stock: int
    description: Optional[str] = None
    is_active: bool


@router.get("", response_model=List[PhoneResponse])
async def get_phones(
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("mobile:read")),
    db: Session = Depends(get_db)
):
    """获取手机列表"""
    logger.info(f"获取手机列表请求 by {current_user.username}")
    
    phones = db.query(Phone).all()
    
    logger.info(f"获取手机列表成功，共 {len(phones)} 个手机")
    return phones


@router.get("/{phone_id}", response_model=PhoneResponse)
async def get_phone(
    phone_id: int,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("mobile:read")),
    db: Session = Depends(get_db)
):
    """获取单个手机"""
    logger.info(f"获取手机请求: {phone_id} by {current_user.username}")
    
    phone = db.query(Phone).filter(Phone.id == phone_id).first()
    if not phone:
        logger.warning(f"获取手机失败 - 手机不存在: {phone_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="手机不存在"
        )
    
    logger.info(f"获取手机成功: {phone.name}")
    return phone


@router.post("", response_model=PhoneResponse)
async def create_phone(
    phone_data: PhoneCreate,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("mobile:create")),
    db: Session = Depends(get_db)
):
    """创建手机"""
    logger.info(f"创建手机请求: {phone_data.name} by {current_user.username}")
    
    # 创建手机
    phone = Phone(
        name=phone_data.name,
        brand=phone_data.brand,
        model=phone_data.model,
        price=phone_data.price,
        stock=phone_data.stock,
        description=phone_data.description,
        is_active=phone_data.is_active
    )
    db.add(phone)
    db.commit()
    db.refresh(phone)
    
    logger.info(f"手机创建成功: {phone.name}")
    return phone


@router.put("/{phone_id}", response_model=PhoneResponse)
async def update_phone(
    phone_id: int,
    phone_data: PhoneUpdate,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("mobile:update")),
    db: Session = Depends(get_db)
):
    """更新手机"""
    logger.info(f"更新手机请求: {phone_id} by {current_user.username}")
    
    phone = db.query(Phone).filter(Phone.id == phone_id).first()
    if not phone:
        logger.warning(f"更新手机失败 - 手机不存在: {phone_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="手机不存在"
        )
    
    # 更新手机信息
    if phone_data.name is not None:
        phone.name = phone_data.name
    if phone_data.brand is not None:
        phone.brand = phone_data.brand
    if phone_data.model is not None:
        phone.model = phone_data.model
    if phone_data.price is not None:
        phone.price = phone_data.price
    if phone_data.stock is not None:
        phone.stock = phone_data.stock
    if phone_data.description is not None:
        phone.description = phone_data.description
    if phone_data.is_active is not None:
        phone.is_active = phone_data.is_active
    
    db.commit()
    db.refresh(phone)
    
    logger.info(f"手机更新成功: {phone.name}")
    return phone


@router.delete("/{phone_id}")
async def delete_phone(
    phone_id: int,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("mobile:delete")),
    db: Session = Depends(get_db)
):
    """删除手机"""
    logger.info(f"删除手机请求: {phone_id} by {current_user.username}")
    
    phone = db.query(Phone).filter(Phone.id == phone_id).first()
    if not phone:
        logger.warning(f"删除手机失败 - 手机不存在: {phone_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="手机不存在"
        )
    
    db.delete(phone)
    db.commit()
    
    logger.info(f"手机删除成功: {phone.name}")
    return {"message": "手机删除成功"}
