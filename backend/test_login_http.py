import http.client
import json
import time

# 测试登录接口
def test_login():
    start_time = time.time()
    conn = http.client.HTTPConnection("localhost", 8000, timeout=10)
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        conn.request("POST", "/api/v1/auth/login", json.dumps(data), headers)
        response = conn.getresponse()
        end_time = time.time()
        print(f"请求耗时: {end_time - start_time:.2f} 秒")
        print(f"状态码: {response.status}")
        print(f"响应: {response.read().decode()}")
        conn.close()
    except Exception as e:
        end_time = time.time()
        print(f"请求耗时: {end_time - start_time:.2f} 秒")
        print(f"错误: {str(e)}")
        conn.close()

if __name__ == "__main__":
    test_login()
