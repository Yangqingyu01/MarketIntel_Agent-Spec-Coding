"""Test login functionality."""

import sys
import json
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
sys.path.append('.')

# 导入应用
from main import app

# 创建测试客户端
client = TestClient(app)

# 测试注册
print("测试注册...")
register_response = client.post(
    "/api/auth/register",
    json={
        "organization_name": "测试组织",
        "full_name": "测试用户",
        "email": "test@example.com",
        "password": "123456"
    }
)
print(f"注册状态码: {register_response.status_code}")
print(f"注册响应: {register_response.json()}")
print()

# 测试登录
print("测试登录...")
login_response = client.post(
    "/api/auth/login",
    json={
        "email": "test@example.com",
        "password": "123456"
    }
)
print(f"登录状态码: {login_response.status_code}")
print(f"登录响应: {login_response.json()}")
print()

# 测试获取用户信息
if login_response.status_code == 200:
    token = login_response.json().get("access_token")
    print("测试获取用户信息...")
    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"
    }
)
    print(f"获取用户信息状态码: {me_response.status_code}")
    print(f"获取用户信息响应: {me_response.json()}")
