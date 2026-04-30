# -*- coding: utf-8 -*-
"""
认证与授权模块 - JWT + RBAC
"""
from datetime import datetime, timedelta, UTC
from typing import Optional, List
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user_model import User, Role, Permission
from app.core.logger import export_logger as logger

# ==================== 配置 ====================
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

security = HTTPBearer()


# ==================== 密码工具 ====================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    # 确保密码长度不超过72字节(bcrypt限制)
    plain_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    # 确保密码长度不超过72字节(bcrypt限制)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


# ==================== JWT工具 ====================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error during token decode: {e}")
        return {}


# ==================== 依赖函数 ====================
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户依赖"""
    token = credentials.credentials
    logger.info(f"收到认证请求，Token前10个字符: {token[:10] if token else 'None'}")
    
    payload = decode_access_token(token)
    
    if not payload:
        logger.warning("无效的认证令牌")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        logger.warning("无法验证凭据，token中缺少sub字段")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logger.warning(f"用户不存在: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.warning(f"用户已被禁用: {username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    logger.info(f"用户认证成功: {username}")
    return user


def check_permission(permission_code: str):
    """权限检查依赖工厂"""
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.has_permission(permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {permission_code}"
            )
        return current_user
    return permission_checker


def check_role(role_code: str):
    """角色检查依赖工厂"""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        user_roles = [role.code for role in current_user.roles if role.is_active]
        if role_code not in user_roles and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少角色: {role_code}"
            )
        return current_user
    return role_checker
