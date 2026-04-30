# -*- coding: utf-8 -*-
"""
公共商品 API 路由（无需权限控制）
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.core.database import get_db
from app.models.user_model import Product
from app.core.logger import export_logger as logger

router = APIRouter()


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


@router.get("/products", response_model=List[ProductResponse])
async def get_public_products(
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort: Optional[str] = Query(None, description="排序方式: price_asc, price_desc, created_new, created_old"),
    db: Session = Depends(get_db)
):
    """获取公共商品列表（无需权限）"""
    logger.info(f"获取公共商品列表请求，搜索: {search}, 排序: {sort}")
    
    # 构建查询，包含图片相关字段
    query = db.query(
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
    )
    
    # 只返回激活状态的商品
    query = query.filter(Product.is_active == True)
    
    # 搜索
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            Product.name.ilike(search_pattern) |
            Product.description.ilike(search_pattern) |
            Product.code.ilike(search_pattern)
        )
    
    # 排序
    if sort == "price_asc":
        query = query.order_by(asc(Product.price))
    elif sort == "price_desc":
        query = query.order_by(desc(Product.price))
    elif sort == "created_new":
        query = query.order_by(desc(Product.created_at))
    elif sort == "created_old":
        query = query.order_by(asc(Product.created_at))
    else:
        # 默认按创建时间倒序
        query = query.order_by(desc(Product.created_at))
    
    products = query.all()
    
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
    
    logger.info(f"获取公共商品列表成功，共 {len(product_list)} 个商品")
    return product_list


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_public_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """获取单个公共商品（无需权限）"""
    logger.info(f"获取公共商品请求: {product_id}")
    
    # 构建查询，包含图片相关字段
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
    ).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        logger.warning(f"获取公共商品失败 - 商品不存在或已下架: {product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在或已下架"
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
    
    logger.info(f"获取公共商品成功: {product.name}")
    return product_dict
