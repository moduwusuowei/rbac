import http.client
import json

# 测试登录接口
def test_login():
    conn = http.client.HTTPConnection("localhost", 8000)
    
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
        print(f"Status Code: {response.status}")
        print(f"Response: {response.read().decode()}")
        conn.close()
    except Exception as e:
        print(f"Error: {str(e)}")
        conn.close()

if __name__ == "__main__":
    test_login()
