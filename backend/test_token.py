# -*- coding: utf-8 -*-
"""
测试JWT token生成和验证
"""
from datetime import datetime, timedelta
from app.core.auth import create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

print(f"Token过期时间: {ACCESS_TOKEN_EXPIRE_MINUTES}分钟")

# 生成token
token = create_access_token(data={"sub": "admin", "user_id": 1})
print(f"生成的token: {token}")

# 解码token
payload = decode_access_token(token)
print(f"解码的payload: {payload}")

# 检查过期时间
exp = payload.get("exp")
if exp:
    exp_time = datetime.fromtimestamp(exp)
    now = datetime.utcnow()
    print(f"过期时间: {exp_time}")
    print(f"当前时间: {now}")
    print(f"是否过期: {exp_time < now}")
    print(f"剩余时间: {(exp_time - now).total_seconds() / 60}分钟")
