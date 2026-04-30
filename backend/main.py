# -*- coding: utf-8 -*-
"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from app.core.database import create_db_and_tables, engine, SessionLocal
from app.core.auth import get_current_user
from app.models.user_model import User, Role, Permission, Product, Phone
from app.core.auth import get_password_hash
from app.routers.api_router import api_router
from app.core.logger import export_logger as logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表和初始数据
    create_db_and_tables()
    create_initial_data()
    yield
    # 关闭时清理资源
    pass


# 创建FastAPI应用
app = FastAPI(
    title="RBAC System API",
    description="基于角色的访问控制系统",
    version="1.0.0",
    lifespan=lifespan
)


# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


# 注册路由
app.include_router(api_router, prefix="/api/v1")

# 配置静态文件服务
upload_dir = os.path.join("uploads")
os.makedirs(upload_dir, exist_ok=True)
os.makedirs(os.path.join(upload_dir, "avatars"), exist_ok=True)
os.makedirs(os.path.join(upload_dir, "images"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# 根路由
@app.get("/")
async def root():
    return {"message": "RBAC System API", "version": "1.0.0"}


# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 测试端点
@app.get("/test")
async def test_endpoint():
    return {"message": "测试成功"}


# ==================== 初始化数据 ====================
def create_initial_data():
    """创建初始数据：超级管理员和普通用户角色"""
    db = SessionLocal()
    try:
        # 检查是否已存在数据
        existing_admin = db.query(Role).filter(Role.code == "admin").first()
        if existing_admin:
            return
        
        # 创建权限
        permissions = [
            Permission(name="用户查看", code="user:read", description="查看用户列表"),
            Permission(name="用户创建", code="user:create", description="创建新用户"),
            Permission(name="用户编辑", code="user:update", description="编辑用户信息"),
            Permission(name="用户删除", code="user:delete", description="删除用户"),
            Permission(name="角色查看", code="role:read", description="查看角色列表"),
            Permission(name="角色管理", code="role:manage", description="管理角色权限"),
            Permission(name="权限查看", code="permission:read", description="查看权限列表"),
            Permission(name="权限管理", code="permission:manage", description="管理权限"),
            Permission(name="商品查看", code="product:read", description="查看商品列表"),
            Permission(name="商品创建", code="product:create", description="创建新商品"),
            Permission(name="商品编辑", code="product:update", description="编辑商品信息"),
            Permission(name="商品删除", code="product:delete", description="删除商品"),
            Permission(name="手机查看", code="mobile:read", description="查看手机列表"),
            Permission(name="手机创建", code="mobile:create", description="创建新手机"),
            Permission(name="手机编辑", code="mobile:update", description="编辑手机信息"),
            Permission(name="手机删除", code="mobile:delete", description="删除手机"),
        ]
        db.add_all(permissions)
        db.flush()
        
        # 创建超级管理员角色
        admin_role = Role(
            name="超级管理员",
            code="admin",
            description="拥有所有权限",
            is_active=True
        )
        admin_role.permissions = permissions
        db.add(admin_role)
        
        # 创建普通用户角色
        user_role = Role(
            name="普通用户",
            code="user",
            description="基础用户权限",
            is_active=True
        )
        user_role.permissions = [
            p for p in permissions if p.code in ["user:read"]
        ]
        db.add(user_role)
        
        # 创建商品角色
        product_role = Role(
            name="商品管理员",
            code="product",
            description="商品管理权限",
            is_active=True
        )
        product_role.permissions = [
            p for p in permissions if p.code in ["product:read", "product:create", "product:update"]
        ]
        db.add(product_role)
        
        # 创建手机角色
        phone_role = Role(
            name="手机管理员",
            code="phone",
            description="手机管理权限",
            is_active=True
        )
        phone_role.permissions = [
            p for p in permissions if p.code in ["mobile:read", "mobile:create", "mobile:update"]
        ]
        db.add(phone_role)
        
        # 创建超级管理员用户
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            email="admin@rbac.local",
            is_active=True,
            is_superuser=True
        )
        admin_user.roles = [admin_role]
        db.add(admin_user)
        
        # 创建普通用户
        normal_user = User(
            username="user",
            password_hash=get_password_hash("user123"),
            email="user@rbac.local",
            is_active=True,
            is_superuser=False
        )
        normal_user.roles = [user_role, phone_role]
        db.add(normal_user)
        
        # 创建一些测试商品数据
        products = [
            Product(
                name="iPhone 15 Pro",
                code="IP15PRO",
                description="苹果最新旗舰手机",
                price=9999.99,
                stock=50,
                is_active=True
            ),
            Product(
                name="MacBook Pro 14",
                code="MBP14",
                description="苹果专业笔记本电脑",
                price=16999.99,
                stock=20,
                is_active=True
            ),
            Product(
                name="AirPods Pro 2",
                code="APP2",
                description="苹果无线降噪耳机",
                price=1899.99,
                stock=100,
                is_active=True
            ),
            Product(
                name="iPad Pro 12.9",
                code="IPDPRO12",
                description="苹果专业平板电脑",
                price=8999.99,
                stock=30,
                is_active=True
            ),
        ]
        db.add_all(products)
        
        # 创建一些测试手机数据
        phones = [
            Phone(
                name="iPhone 15",
                brand="Apple",
                model="iPhone 15",
                price=6999.99,
                stock=100,
                description="苹果最新智能手机",
                is_active=True
            ),
            Phone(
                name="iPhone 15 Plus",
                brand="Apple",
                model="iPhone 15 Plus",
                price=7999.99,
                stock=80,
                description="苹果大屏智能手机",
                is_active=True
            ),
            Phone(
                name="iPhone 15 Pro Max",
                brand="Apple",
                model="iPhone 15 Pro Max",
                price=10999.99,
                stock=40,
                description="苹果顶级旗舰手机",
                is_active=True
            ),
        ]
        db.add_all(phones)
        
        db.commit()
        logger.info("✓ 初始化数据创建完成")
        logger.info("  - 超级管理员: admin / admin123")
        logger.info("  - 普通用户: user / user123")
        logger.info("  - 创建了 4 个测试商品")
        logger.info("  - 创建了 3 个测试手机")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
