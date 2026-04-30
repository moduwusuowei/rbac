# -*- coding: utf-8 -*-
"""
数据库模型层 - 使用 SQLAlchemy Declarative Base
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, func, Float
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column


# ==================== 基础模型 ====================
class Base(DeclarativeBase):
    """基础模型"""
    pass


# ==================== 关联表 ====================
# 用户-角色关联表
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

# 角色-权限关联表
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

# 用户-组关联表
user_groups = Table(
    "user_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
)


# ==================== 组模型 ====================
class Group(Base):
    """用户组表"""
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="组名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="组编码")
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="组描述")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    leader_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="组长ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    users: Mapped[List["User"]] = relationship("User", secondary=user_groups, back_populates="groups")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="group")
    leader: Mapped[Optional["User"]] = relationship("User", foreign_keys=[leader_id])


# ==================== 权限模型 ====================
class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="权限名称，如: user:create")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="权限编码，如: user_create")
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="权限描述")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    roles: Mapped[List["Role"]] = relationship("Role", secondary=role_permissions, back_populates="permissions")


# ==================== 角色模型 ====================
class Role(Base):
    """角色表"""
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色编码")
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="角色描述")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    users: Mapped[List["User"]] = relationship("User", secondary=user_roles, back_populates="roles")
    permissions: Mapped[List[Permission]] = relationship("Permission", secondary=role_permissions, back_populates="roles")


# ==================== 用户模型 ====================
class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="邮箱")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="手机号")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否为超级管理员")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="用户头像URL")
    avatar_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="用户头像存储路径")
    avatar_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="用户头像唯一标识符")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    roles: Mapped[List[Role]] = relationship("Role", secondary=user_roles, back_populates="users")
    groups: Mapped[List[Group]] = relationship("Group", secondary=user_groups, back_populates="users")
    
    def get_all_permissions(self) -> set:
        """获取用户所有权限"""
        permissions = set()
        for role in self.roles:
            if role.is_active:
                for permission in role.permissions:
                    permissions.add(permission.code)
        return permissions
    
    def has_permission(self, permission_code: str) -> bool:
        """检查用户是否拥有特定权限"""
        # 超级管理员拥有所有权限
        if self.is_superuser:
            return True
        return permission_code in self.get_all_permissions()


# ==================== 商品模型 ====================
class Product(Base):
    """商品表"""
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="商品名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="商品编码")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="商品描述")
    price: Mapped[float] = mapped_column(Float, nullable=False, comment="商品价格")
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="商品库存")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="商品图片URL")
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="商品图片存储路径")
    image_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="商品图片唯一标识符")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


# ==================== 任务模型 ====================
class Task(Base):
    """任务表"""
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="任务标题")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="任务描述")
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="任务状态: pending, in_progress, completed, cancelled")
    priority: Mapped[str] = mapped_column(String(20), default="medium", comment="任务优先级: low, medium, high")
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="开始日期")
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="截止日期")
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), comment="创建人ID")
    group_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), comment="所属组ID")
    assigned_to: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), comment="指派给")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id])
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to])
    group: Mapped[Optional[Group]] = relationship("Group", back_populates="tasks")


# ==================== 手机模型 ====================
class Phone(Base):
    """手机表"""
    __tablename__ = "phones"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="手机名称")
    brand: Mapped[str] = mapped_column(String(50), nullable=False, comment="品牌")
    model: Mapped[str] = mapped_column(String(50), nullable=False, comment="型号")
    price: Mapped[float] = mapped_column(Float, nullable=False, comment="价格")
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="库存")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="描述")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
