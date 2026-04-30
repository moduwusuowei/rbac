# -*- coding: utf-8 -*-
"""
认证 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.models.user_model import User
from app.schemas.auth import TokenResponse, LoginRequest, RegisterRequest, RegisterResponse, ChangePasswordRequest, ChangePasswordResponse
from app.core.logger import export_logger as logger

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """用户登录"""
    logger.info(f"登录尝试: {login_data.username}")
    
    # 查找用户
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user:
        logger.warning(f"登录失败 - 用户不存在: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(login_data.password, user.password_hash):
        logger.warning(f"登录失败 - 密码错误: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查账户状态
    if not user.is_active:
        logger.warning(f"登录失败 - 账户已被禁用: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    # 生成Token
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    logger.info(f"登录成功: {login_data.username}")
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_info={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "roles": [role.code for role in user.roles],
            "permissions": list(user.get_all_permissions())
        }
    )


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_superuser": current_user.is_superuser,
        "avatar_url": current_user.avatar_url,
        "roles": [role.code for role in current_user.roles],
        "permissions": list(current_user.get_all_permissions())
    }


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统统计数据"""
    from app.models.user_model import Role, Permission
    
    user_count = db.query(User).count()
    role_count = db.query(Role).count()
    permission_count = db.query(Permission).count()
    
    return {
        "user_count": user_count,
        "role_count": role_count,
        "permission_count": permission_count
    }


@router.post("/register", response_model=RegisterResponse)
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """用户注册"""
    logger.info(f"注册尝试: {register_data.username}")
    
    # 验证密码是否匹配
    if register_data.password != register_data.confirm_password:
        logger.warning(f"注册失败 - 密码不匹配: {register_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码和确认密码不匹配"
        )
    
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == register_data.username).first():
        logger.warning(f"注册失败 - 用户名已存在: {register_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == register_data.email).first():
        logger.warning(f"注册失败 - 邮箱已存在: {register_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 加密密码
    password_hash = get_password_hash(register_data.password)
    
    # 创建新用户
    new_user = User(
        username=register_data.username,
        email=register_data.email,
        password_hash=password_hash,
        is_active=True,
        is_superuser=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"注册成功: {register_data.username}")
    return RegisterResponse(
        message="注册成功",
        user_id=new_user.id,
        username=new_user.username,
        email=new_user.email
    )


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    logger.info(f"修改密码请求 by {current_user.username}")

    # 验证当前密码
    if not verify_password(password_data.current_password, current_user.password_hash):
        logger.warning(f"修改密码失败 - 当前密码错误: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )

    # 验证新密码与确认密码是否一致
    if password_data.new_password != password_data.confirm_password:
        logger.warning(f"修改密码失败 - 新密码与确认密码不一致: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码与确认密码不一致"
        )

    # 验证新密码复杂度
    password_errors = []
    if len(password_data.new_password) < 8:
        password_errors.append("长度不能少于8个字符")
    if not any(c.isupper() for c in password_data.new_password):
        password_errors.append("必须包含大写字母")
    if not any(c.islower() for c in password_data.new_password):
        password_errors.append("必须包含小写字母")
    if not any(c.isdigit() for c in password_data.new_password):
        password_errors.append("必须包含数字")
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password_data.new_password):
        password_errors.append("必须包含特殊符号(!@#$%^&*等)")

    if password_errors:
        error_message = "密码必须满足以下要求：" + "；".join(password_errors)
        logger.warning(f"修改密码失败 - 密码复杂度不足: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # 检查新密码是否与当前密码相同
    if password_data.current_password == password_data.new_password:
        logger.warning(f"修改密码失败 - 新密码不能与当前密码相同: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与当前密码相同"
        )

    # 加密新密码
    new_password_hash = get_password_hash(password_data.new_password)

    # 更新密码
    current_user.password_hash = new_password_hash
    db.commit()

    logger.info(f"修改密码成功: {current_user.username}")
    return ChangePasswordResponse(
        message="密码修改成功",
        success=True
    )