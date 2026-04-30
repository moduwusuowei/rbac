# -*- coding: utf-8 -*-
"""
商品管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime
from PIL import Image
from app.core.database import get_db
from app.core.auth import get_current_user, check_permission
from app.models.user_model import User, Product
from app.core.logger import export_logger as logger

router = APIRouter()


class ProductCreate(BaseModel):
    """创建商品请求"""
    name: str
    code: str
    description: Optional[str] = None
    price: float
    stock: int
    is_active: bool = True
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    image_id: Optional[str] = None


class ProductUpdate(BaseModel):
    """更新商品请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    image_id: Optional[str] = None


class ProductResponse(BaseModel):
    """商品响应"""
    model_config = {"from_attributes": True}
    
    id: int
    name: str
    code: str
    description: Optional[str] = None
    price: float
    stock: int
    is_active: bool
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    image_id: Optional[str] = None

    @classmethod
    def from_orm(cls, db_product):
        """从数据库模型创建响应对象"""
        # 检查数据库模型是否有图片相关字段
        data = {
            "id": db_product.id,
            "name": db_product.name,
            "code": db_product.code,
            "description": db_product.description,
            "price": db_product.price,
            "stock": db_product.stock,
            "is_active": db_product.is_active,
            "image_url": getattr(db_product, "image_url", None),
            "image_path": getattr(db_product, "image_path", None),
            "image_id": getattr(db_product, "image_id", None)
        }
        return cls(**data)


@router.get("", response_model=List[ProductResponse])
async def get_products(
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("product:read")),
    db: Session = Depends(get_db)
):
    """获取商品列表"""
    logger.info(f"获取商品列表请求 by {current_user.username}")
    
    # 查询数据库中存在的字段，包括图片相关字段
    products = db.query(
        Product.id,
        Product.name,
        Product.code,
        Product.description,
        Product.price,
        Product.stock,
        Product.is_active,
        Product.image_url,
        Product.image_path,
        Product.image_id
    ).all()

    # 转换为字典列表
    product_list = []
    for product in products:
        product_dict = {
            "id": product.id,
            "name": product.name,
            "code": product.code,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "is_active": product.is_active,
            "image_url": product.image_url,
            "image_path": product.image_path,
            "image_id": product.image_id
        }
        product_list.append(product_dict)
    
    logger.info(f"获取商品列表成功，共 {len(product_list)} 个商品")
    return product_list


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("product:read")),
    db: Session = Depends(get_db)
):
    """获取单个商品"""
    logger.info(f"获取商品请求: {product_id} by {current_user.username}")
    
    # 查询数据库中存在的字段，包括图片相关字段
    product = db.query(
        Product.id,
        Product.name,
        Product.code,
        Product.description,
        Product.price,
        Product.stock,
        Product.is_active,
        Product.image_url,
        Product.image_path,
        Product.image_id
    ).filter(Product.id == product_id).first()

    if not product:
        logger.warning(f"获取商品失败 - 商品不存在: {product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    # 转换为字典
    product_dict = {
        "id": product.id,
        "name": product.name,
        "code": product.code,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "is_active": product.is_active,
        "image_url": product.image_url,
        "image_path": product.image_path,
        "image_id": product.image_id
    }
    
    logger.info(f"获取商品成功: {product.name}")
    return product_dict


@router.post("", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("product:create")),
    db: Session = Depends(get_db)
):
    """创建商品"""
    logger.info(f"创建商品请求: {product_data.name} by {current_user.username}")
    
    # 检查商品编码是否已存在
    existing = db.query(Product.id).filter(Product.code == product_data.code).first()
    if existing:
        logger.warning(f"创建商品失败 - 商品编码已存在: {product_data.code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="商品编码已存在"
        )
    
    # 创建商品
    product = Product(
        name=product_data.name,
        code=product_data.code,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        is_active=product_data.is_active,
        image_url=product_data.image_url,
        image_path=product_data.image_path,
        image_id=product_data.image_id
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # 构建响应，包含图片相关字段
    product_dict = {
        "id": product.id,
        "name": product.name,
        "code": product.code,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "is_active": product.is_active,
        "image_url": getattr(product, "image_url", None),
        "image_path": getattr(product, "image_path", None),
        "image_id": getattr(product, "image_id", None)
    }
    
    logger.info(f"商品创建成功: {product.name}")
    return product_dict


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("product:update")),
    db: Session = Depends(get_db)
):
    """更新商品"""
    logger.info(f"更新商品请求: {product_id} by {current_user.username}")
    
    # 查询完整的商品模型对象
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"更新商品失败 - 商品不存在: {product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 更新商品信息
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.price is not None:
        product.price = product_data.price
    if product_data.stock is not None:
        product.stock = product_data.stock
    if product_data.is_active is not None:
        product.is_active = product_data.is_active
    if product_data.image_url is not None:
        product.image_url = product_data.image_url
    if product_data.image_path is not None:
        product.image_path = product_data.image_path
    if product_data.image_id is not None:
        product.image_id = product_data.image_id

    db.commit()
    db.refresh(product)

    # 构建响应，包含图片相关字段
    product_dict = {
        "id": product.id,
        "name": product.name,
        "code": product.code,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "is_active": product.is_active,
        "image_url": getattr(product, "image_url", None),
        "image_path": getattr(product, "image_path", None),
        "image_id": getattr(product, "image_id", None)
    }
    
    logger.info(f"商品更新成功: {product.name}")
    return product_dict


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    _: User = Depends(check_permission("product:delete")),
    db: Session = Depends(get_db)
):
    """删除商品"""
    logger.info(f"删除商品请求: {product_id} by {current_user.username}")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"删除商品失败 - 商品不存在: {product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    db.delete(product)
    db.commit()
    
    logger.info(f"商品删除成功: {product.name}")
    return {"message": "商品删除成功"}



