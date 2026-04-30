import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    from app.main import app
    print("✅ 导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")