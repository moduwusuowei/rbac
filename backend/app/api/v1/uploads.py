# -*- coding: utf-8 -*-
"""
通用文件上传 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import uuid
from app.core.database import get_db
from app.core.auth import get_current_user, check_permission
from app.models.user_model import User
from app.core.logger import export_logger as logger

router = APIRouter()


class ImageUploadResponse(BaseModel):
    """图片上传响应"""
    image_url: str
    image_path: str
    image_id: str
    message: str


@router.post("/image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传图片（通用接口）"""
    logger.info(f"上传图片请求 by {current_user.username}")
    
    # 验证文件类型
    allowed_extensions = {"jpg", "jpeg", "png", "webp"}
    file_extension = os.path.splitext(file.filename)[1].lower().lstrip(".")
    if file_extension not in allowed_extensions:
        logger.warning(f"上传失败 - 文件类型不支持: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持 JPG、PNG、WEBP 格式的图片"
        )
    
    # 验证文件大小（不超过5MB）
    file_size = 0
    contents = await file.read()
    file_size = len(contents)
    if file_size > 5 * 1024 * 1024:
        logger.warning(f"上传失败 - 文件过大: {file_size} bytes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片大小不能超过5MB"
        )
    
    # 验证图片分辨率（不低于800×800像素）
    try:
        from PIL import Image
        import io
        # 使用BytesIO创建文件对象，避免文件指针问题
        image = Image.open(io.BytesIO(contents))
        width, height = image.size
        if width < 800 or height < 800:
            logger.warning(f"上传失败 - 分辨率不足: {width}×{height}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图片分辨率建议不低于800×800像素"
            )
    except Exception as e:
        logger.error(f"上传失败 - 图片验证错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的图片文件"
        )
    
    # 生成唯一标识符
    image_id = str(uuid.uuid4())
    
    # 创建存储目录
    upload_dir = os.path.join("uploads", "images")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成文件名
    filename = f"{image_id}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.error(f"上传失败 - 文件保存错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件上传失败，请重试"
        )
    
    # 生成访问URL（使用完整的后端服务器地址）
    image_url = f"http://localhost:8000/uploads/images/{filename}"
    
    logger.info(f"图片上传成功: {image_id}")
    
    return ImageUploadResponse(
        image_url=image_url,
        image_path=file_path,
        image_id=image_id,
        message="图片上传成功"
    )


@router.post("/avatar", response_model=ImageUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传用户头像"""
    logger.info(f"上传头像请求 by {current_user.username}")
    
    # 验证文件类型
    allowed_extensions = {"jpg", "jpeg", "png", "webp", "gif"}
    file_extension = os.path.splitext(file.filename)[1].lower().lstrip(".")
    if file_extension not in allowed_extensions:
        logger.warning(f"上传失败 - 文件类型不支持: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持 JPG、PNG、WEBP、GIF 格式的图片"
        )
    
    # 验证文件大小（不超过2MB）
    file_size = 0
    contents = await file.read()
    file_size = len(contents)
    if file_size > 2 * 1024 * 1024:
        logger.warning(f"上传失败 - 文件过大: {file_size} bytes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像大小不能超过2MB"
        )
    
    # 验证图片分辨率（不限制太低，允许100x100以上）
    try:
        from PIL import Image
        image = Image.open(file.file)
        width, height = image.size
        if width < 100 or height < 100:
            logger.warning(f"上传失败 - 分辨率不足: {width}×{height}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="头像分辨率不能低于100×100像素"
            )
    except Exception as e:
        logger.error(f"上传失败 - 图片验证错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的图片文件"
        )
    
    # 生成唯一标识符
    image_id = str(uuid.uuid4())
    
    # 创建存储目录
    upload_dir = os.path.join("uploads", "avatars")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成文件名
    filename = f"{current_user.id}_{image_id}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.error(f"上传失败 - 文件保存错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件上传失败，请重试"
        )
    
    # 生成访问URL
    image_url = f"http://localhost:8000/uploads/avatars/{filename}"
    
    # 更新用户头像信息
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        user.avatar_url = image_url
        user.avatar_path = file_path
        user.avatar_id = image_id
        db.commit()
    
    logger.info(f"头像上传成功: {image_id} for user {current_user.username}")
    
    return ImageUploadResponse(
        image_url=image_url,
        image_path=file_path,
        image_id=image_id,
        message="头像上传成功"
    )
