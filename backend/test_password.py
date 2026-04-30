# -*- coding: utf-8 -*-
"""
测试密码验证
"""
from app.core.auth import verify_password, get_password_hash

# 测试密码验证
print("测试密码验证...")

# 测试1：验证已知密码
print("\n1. 测试已知密码:")
admin_hash = "$2b$12$.zDDpR00NMGPVovrE0gszOaEYz0qnRv6q8WQUBFrTQJqDoIvqCDny"
user_hash = "$2b$12$OAQLQ32O8gdvtQ3j28k7VOSLWaOaAmWy73kWApLzbO48YLjJayQLu"
user1111_hash = "$2b$12$2cDT.BNLGXXe/miPQdyXVObdCXIfKZ4qd20qJl1OAN1StqQFCR72m"

print(f"admin密码验证: {verify_password('admin', admin_hash)}")
print(f"user密码验证: {verify_password('user', user_hash)}")
print(f"1111密码验证: {verify_password('1111', user1111_hash)}")

# 测试2：测试密码哈希生成
print("\n2. 测试密码哈希生成:")
test_password = "test123"
hashed = get_password_hash(test_password)
print(f"原始密码: {test_password}")
print(f"哈希值: {hashed}")
print(f"验证: {verify_password(test_password, hashed)}")

print("\n测试完成！")
