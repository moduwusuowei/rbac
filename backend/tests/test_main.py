"""
RBAC系统综合测试套件
涵盖：认证、用户管理、组管理、任务管理等核心功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt

from main import app
from app.models.user_model import Base, User, Group, Task
from app.core.database import get_db
from app.core.auth import create_access_token

def hash_password(password: str) -> str:
    """使用bcrypt哈希密码（与应用一致）"""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

TEST_DATABASE_URL = "sqlite:///./test_rbac.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    """初始化测试数据库"""
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # 创建admin用户（超级管理员）
    admin_user = User(
        username="admin",
        email="admin@test.com",
        password_hash=hash_password("Admin@123"),
        is_active=True,
        is_superuser=True
    )
    db.add(admin_user)
    
    # 创建普通用户
    test_user = User(
        username="testuser",
        email="test@test.com",
        password_hash=hash_password("Test@123"),
        is_active=True
    )
    db.add(test_user)
    
    # 创建第二个普通用户
    test_user2 = User(
        username="testuser2",
        email="testuser2@test.com",
        password_hash=hash_password("Test2@123"),
        is_active=True
    )
    db.add(test_user2)
    
    # 创建禁用用户
    disabled_user = User(
        username="disabled",
        email="disabled@test.com",
        password_hash=hash_password("Disabled@123"),
        is_active=False
    )
    db.add(disabled_user)
    
    db.commit()
    db.refresh(admin_user)
    db.refresh(test_user)
    db.refresh(test_user2)
    db.refresh(disabled_user)
    
    yield
    
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def admin_token():
    """获取管理员token"""
    token = create_access_token(data={"sub": "admin"})
    return f"Bearer {token}"

@pytest.fixture(scope="module")
def user_token():
    """获取普通用户token"""
    token = create_access_token(data={"sub": "testuser"})
    return f"Bearer {token}"

@pytest.fixture(scope="module")
def user2_token():
    """获取第二个普通用户token"""
    token = create_access_token(data={"sub": "testuser2"})
    return f"Bearer {token}"

# ==================== 认证测试 ====================

def test_login_success(setup_database):
    """测试登录成功"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin@123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure_wrong_password():
    """测试登录失败-密码错误"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_login_failure_user_not_found():
    """测试登录失败-用户不存在"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "password123"}
    )
    assert response.status_code == 401

def test_login_failure_disabled_user(setup_database):
    """测试登录失败-账户已禁用"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "disabled", "password": "Disabled@123"}
    )
    assert response.status_code == 403

def test_unauthorized_access():
    """测试未授权访问"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_get_current_user(setup_database, admin_token):
    """测试获取当前用户信息"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "admin"

def test_get_stats(setup_database, admin_token):
    """测试获取系统统计数据"""
    response = client.get(
        "/api/v1/auth/stats",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert "user_count" in response.json()
    assert "role_count" in response.json()
    assert "permission_count" in response.json()

def test_register_success(setup_database):
    """测试用户注册成功"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "NewPass@123",
            "confirm_password": "NewPass@123"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "注册成功"

def test_register_failure_password_mismatch():
    """测试注册失败-密码不匹配"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser3",
            "email": "test3@example.com",
            "password": "Password@123",
            "confirm_password": "Different@123"
        }
    )
    assert response.status_code == 400

def test_register_failure_username_exists(setup_database):
    """测试注册失败-用户名已存在"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "admin",
            "email": "another@example.com",
            "password": "Password@123",
            "confirm_password": "Password@123"
        }
    )
    assert response.status_code == 400

def test_change_password_success(setup_database, admin_token):
    """测试修改密码成功"""
    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "Admin@123",
            "new_password": "NewAdmin@456",
            "confirm_password": "NewAdmin@456"
        },
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "密码修改成功"

def test_change_password_failure_wrong_current(setup_database, admin_token):
    """测试修改密码失败-当前密码错误"""
    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "Wrong@123",
            "new_password": "NewAdmin@456",
            "confirm_password": "NewAdmin@456"
        },
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 400

def test_change_password_failure_same_as_current(setup_database, admin_token):
    """测试修改密码失败-新密码与当前密码相同"""
    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "NewAdmin@456",
            "new_password": "NewAdmin@456",
            "confirm_password": "NewAdmin@456"
        },
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 400

# ==================== 组管理测试 ====================

def test_create_group(setup_database, admin_token):
    """测试创建组"""
    response = client.post(
        "/api/v1/groups/",
        json={"name": "测试组", "code": "test001", "description": "测试描述"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "测试组"

def test_create_group_failure_duplicate(setup_database, admin_token):
    """测试创建组失败-重复名称"""
    response = client.post(
        "/api/v1/groups/",
        json={"name": "测试组", "code": "test002", "description": "重复测试"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 400

def test_get_groups(setup_database, admin_token):
    """测试获取组列表"""
    response = client.get(
        "/api/v1/groups/",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_group_detail(setup_database, admin_token):
    """测试获取组详情"""
    groups = client.get("/api/v1/groups/", headers={"Authorization": admin_token}).json()
    if groups:
        group_id = groups[0]["id"]
        response = client.get(
            f"/api/v1/groups/{group_id}",
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["id"] == group_id

def test_get_group_detail_forbidden(setup_database, user_token):
    """测试获取组详情失败-无权访问"""
    # 普通用户没有加入任何组，尝试访问不存在的组
    response = client.get(
        "/api/v1/groups/999",
        headers={"Authorization": user_token}
    )
    assert response.status_code == 404

def test_update_group(setup_database, admin_token):
    """测试更新组"""
    groups = client.get("/api/v1/groups/", headers={"Authorization": admin_token}).json()
    if groups:
        group_id = groups[0]["id"]
        response = client.put(
            f"/api/v1/groups/{group_id}",
            json={"name": "更新后的组名", "description": "更新后的描述"},
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "更新后的组名"

def test_update_group_forbidden(setup_database, user_token):
    """测试更新组失败-非组长"""
    # 普通用户尝试更新组
    response = client.put(
        "/api/v1/groups/1",
        json={"name": "恶意修改"},
        headers={"Authorization": user_token}
    )
    assert response.status_code == 403 or response.status_code == 404

def test_add_member(setup_database, admin_token):
    """测试添加成员"""
    groups = client.get("/api/v1/groups/", headers={"Authorization": admin_token}).json()
    if groups:
        group_id = groups[0]["id"]
        response = client.post(
            f"/api/v1/groups/{group_id}/members",
            json={"username": "testuser"},
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200

def test_add_member_failure_already_in_group(setup_database, admin_token):
    """测试添加成员失败-已在组内"""
    groups = client.get("/api/v1/groups/", headers={"Authorization": admin_token}).json()
    if groups:
        group_id = groups[0]["id"]
        response = client.post(
            f"/api/v1/groups/{group_id}/members",
            json={"username": "testuser"},
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 400

def test_add_member_failure_not_leader(setup_database, user_token):
    """测试添加成员失败-非组长"""
    response = client.post(
        "/api/v1/groups/1/members",
        json={"username": "testuser2"},
        headers={"Authorization": user_token}
    )
    assert response.status_code == 403 or response.status_code == 404

def test_add_member_failure_user_not_found(setup_database, admin_token):
    """测试添加成员失败-用户不存在"""
    groups = client.get("/api/v1/groups/", headers={"Authorization": admin_token}).json()
    if groups:
        group_id = groups[0]["id"]
        response = client.post(
            f"/api/v1/groups/{group_id}/members",
            json={"username": "nonexistent"},
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 404

def test_remove_member(setup_database, admin_token):
    """测试移除成员"""
    # 先添加第二个用户到组
    groups = client.get("/api/v1/groups/", headers={"Authorization": admin_token}).json()
    if groups:
        group_id = groups[0]["id"]
        # 添加testuser2
        client.post(
            f"/api/v1/groups/{group_id}/members",
            json={"username": "testuser2"},
            headers={"Authorization": admin_token}
        )
        # 获取组成员
        group_detail = client.get(f"/api/v1/groups/{group_id}", headers={"Authorization": admin_token}).json()
        member_ids = [m["id"] for m in group_detail["members"] if m["username"] == "testuser2"]
        if member_ids:
            response = client.delete(
                f"/api/v1/groups/{group_id}/members/{member_ids[0]}",
                headers={"Authorization": admin_token}
            )
            assert response.status_code == 200

def test_remove_member_failure_remove_self(setup_database, admin_token):
    """测试移除成员失败-不能移除自己"""
    groups = client.get("/api/v1/groups/", headers={"Authorization": admin_token}).json()
    if groups:
        group_id = groups[0]["id"]
        # 获取管理员的用户ID
        user_info = client.get("/api/v1/auth/me", headers={"Authorization": admin_token}).json()
        admin_id = user_info["id"]
        response = client.delete(
            f"/api/v1/groups/{group_id}/members/{admin_id}",
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 400

def test_transfer_leadership(setup_database, admin_token):
    """测试交接组长权限"""
    groups = client.get("/api/v1/groups/", headers={"Authorization": admin_token}).json()
    if groups:
        group_id = groups[0]["id"]
        response = client.post(
            f"/api/v1/groups/{group_id}/transfer-leadership",
            json={"username": "testuser"},
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "组长权限交接成功"

def test_transfer_leadership_failure_not_leader(setup_database, user_token):
    """测试交接组长失败-非组长或用户不在组内"""
    response = client.post(
        "/api/v1/groups/1/transfer-leadership",
        json={"username": "testuser2"},
        headers={"Authorization": user_token}
    )
    # 可能的状态码：403(非组长), 404(组不存在), 400(用户不在组内)
    assert response.status_code in [400, 403, 404]

# ==================== 任务管理测试 ====================

def test_create_task(setup_database, admin_token):
    """测试创建任务"""
    response = client.post(
        "/api/v1/tasks/",
        json={"title": "测试任务", "description": "测试描述", "status": "pending", "priority": "medium"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "测试任务"

def test_create_task_with_dates(setup_database, admin_token):
    """测试创建任务（带日期）"""
    response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "带日期任务", 
            "description": "测试日期字段", 
            "status": "pending", 
            "priority": "high",
            "start_date": "2024-01-01T00:00:00",
            "due_date": "2024-12-31T23:59:59"
        },
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200

def test_get_tasks(setup_database, admin_token):
    """测试获取任务列表"""
    response = client.get(
        "/api/v1/tasks/",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_tasks_filter_status(setup_database, admin_token):
    """测试按状态筛选任务"""
    response = client.get(
        "/api/v1/tasks/?status=pending",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200

def test_get_task_detail(setup_database, admin_token):
    """测试获取任务详情"""
    tasks = client.get("/api/v1/tasks/", headers={"Authorization": admin_token}).json()
    if tasks:
        task_id = tasks[0]["id"]
        response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["id"] == task_id

def test_get_task_detail_not_found(setup_database, admin_token):
    """测试获取任务详情失败-任务不存在"""
    response = client.get(
        "/api/v1/tasks/999",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_update_task(setup_database, admin_token):
    """测试更新任务"""
    tasks = client.get("/api/v1/tasks/", headers={"Authorization": admin_token}).json()
    if tasks:
        task_id = tasks[0]["id"]
        response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "更新后的任务", "status": "in_progress"},
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "更新后的任务"

def test_delete_task(setup_database, admin_token):
    """测试删除任务"""
    tasks = client.get("/api/v1/tasks/", headers={"Authorization": admin_token}).json()
    if tasks:
        task_id = tasks[0]["id"]
        response = client.delete(
            f"/api/v1/tasks/{task_id}",
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200

def test_delete_task_not_found(setup_database, admin_token):
    """测试删除任务失败-任务不存在"""
    response = client.delete(
        "/api/v1/tasks/999",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

# ==================== 权限测试 ====================

def test_admin_access(setup_database, admin_token):
    """测试管理员访问权限"""
    response = client.get("/api/v1/groups/", headers={"Authorization": admin_token})
    assert response.status_code == 200

def test_user_access(user_token):
    """测试普通用户访问"""
    response = client.get("/api/v1/groups/", headers={"Authorization": user_token})
    assert response.status_code == 200

# ==================== 角色管理测试 ====================

def test_create_role(setup_database, admin_token):
    """测试创建角色"""
    response = client.post(
        "/api/v1/roles/",
        json={"name": "测试角色", "code": "test_role", "description": "测试描述"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "测试角色"
    assert response.json()["code"] == "test_role"

def test_create_role_failure_duplicate_code(setup_database, admin_token):
    """测试创建角色失败-编码重复"""
    response = client.post(
        "/api/v1/roles/",
        json={"name": "重复角色", "code": "test_role", "description": "重复编码"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 400

def test_get_roles(setup_database, admin_token):
    """测试获取角色列表"""
    response = client.get(
        "/api/v1/roles/",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_role(setup_database, admin_token):
    """测试获取单个角色"""
    roles = client.get("/api/v1/roles/", headers={"Authorization": admin_token}).json()
    if roles:
        role_id = roles[0]["id"]
        response = client.get(
            f"/api/v1/roles/{role_id}",
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["id"] == role_id

def test_get_role_not_found(setup_database, admin_token):
    """测试获取角色失败-角色不存在"""
    response = client.get(
        "/api/v1/roles/999",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_update_role(setup_database, admin_token):
    """测试更新角色"""
    roles = client.get("/api/v1/roles/", headers={"Authorization": admin_token}).json()
    if roles:
        role_id = roles[0]["id"]
        role_code = roles[0]["code"]
        response = client.put(
            f"/api/v1/roles/{role_id}",
            json={"name": "更新角色", "code": role_code, "description": "更新描述"},
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "更新角色"

def test_update_role_not_found(setup_database, admin_token):
    """测试更新角色失败-角色不存在"""
    response = client.put(
        "/api/v1/roles/999",
        json={"name": "更新角色", "code": "test_role"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_delete_role(setup_database, admin_token):
    """测试删除角色"""
    # 创建一个新角色用于删除测试
    response = client.post(
        "/api/v1/roles/",
        json={"name": "待删除角色", "code": "delete_role", "description": "待删除"},
        headers={"Authorization": admin_token}
    )
    role_id = response.json()["id"]
    
    # 删除角色
    delete_response = client.delete(
        f"/api/v1/roles/{role_id}",
        headers={"Authorization": admin_token}
    )
    assert delete_response.status_code == 200

def test_delete_role_not_found(setup_database, admin_token):
    """测试删除角色失败-角色不存在"""
    response = client.delete(
        "/api/v1/roles/999",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_delete_role_with_users(setup_database, admin_token):
    """测试删除角色失败-角色已被使用"""
    # 创建角色
    role_response = client.post(
        "/api/v1/roles/",
        json={"name": "已使用角色", "code": "used_role", "description": "已分配"},
        headers={"Authorization": admin_token}
    )
    role_id = role_response.json()["id"]
    
    # 创建用户并分配角色
    user_response = client.post(
        "/api/v1/users/",
        json={"username": "roleuser", "email": "role@test.com", "password": "Pass@123", "role_ids": [role_id]},
        headers={"Authorization": admin_token}
    )
    
    # 尝试删除角色
    delete_response = client.delete(
        f"/api/v1/roles/{role_id}",
        headers={"Authorization": admin_token}
    )
    assert delete_response.status_code == 400

# ==================== 用户管理测试 ====================

def test_create_user(setup_database, admin_token):
    """测试创建用户"""
    response = client.post(
        "/api/v1/users/",
        json={"username": "newadmin", "email": "newadmin@test.com", "password": "NewAdmin@123"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newadmin"

def test_create_user_failure_duplicate(setup_database, admin_token):
    """测试创建用户失败-用户名重复"""
    response = client.post(
        "/api/v1/users/",
        json={"username": "admin", "email": "another@test.com", "password": "Pass@123"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 400

def test_get_users(setup_database, admin_token):
    """测试获取用户列表"""
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_user(setup_database, admin_token):
    """测试获取单个用户"""
    users = client.get("/api/v1/users/", headers={"Authorization": admin_token}).json()
    if users:
        user_id = users[0]["id"]
        response = client.get(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["id"] == user_id

def test_get_user_not_found(setup_database, admin_token):
    """测试获取用户失败-用户不存在"""
    response = client.get(
        "/api/v1/users/999",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_update_user(setup_database, admin_token):
    """测试更新用户"""
    users = client.get("/api/v1/users/", headers={"Authorization": admin_token}).json()
    if users:
        user_id = users[-1]["id"]  # 选择最后创建的用户
        response = client.put(
            f"/api/v1/users/{user_id}",
            json={"email": "updated@test.com"},
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "updated@test.com"

def test_update_user_not_found(setup_database, admin_token):
    """测试更新用户失败-用户不存在"""
    response = client.put(
        "/api/v1/users/999",
        json={"email": "update@test.com"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_delete_user(setup_database, admin_token):
    """测试删除用户"""
    # 创建一个新用户用于删除测试
    user_response = client.post(
        "/api/v1/users/",
        json={"username": "deleteuser", "email": "delete@test.com", "password": "Pass@123"},
        headers={"Authorization": admin_token}
    )
    user_id = user_response.json()["id"]
    
    # 删除用户
    delete_response = client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": admin_token}
    )
    assert delete_response.status_code == 200

def test_delete_user_not_found(setup_database, admin_token):
    """测试删除用户失败-用户不存在"""
    response = client.delete(
        "/api/v1/users/999",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_delete_current_user(setup_database, admin_token):
    """测试删除用户失败-不能删除自己"""
    # 获取当前用户信息
    user_info = client.get("/api/v1/auth/me", headers={"Authorization": admin_token}).json()
    user_id = user_info["id"]
    
    # 尝试删除自己
    response = client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 400

# ==================== 权限管理测试 ====================

def test_create_permission(setup_database, admin_token):
    """测试创建权限"""
    response = client.post(
        "/api/v1/permissions/",
        json={"name": "测试权限", "code": "test:permission", "description": "测试描述"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "测试权限"
    assert response.json()["code"] == "test:permission"

def test_create_permission_failure_duplicate(setup_database, admin_token):
    """测试创建权限失败-编码重复"""
    response = client.post(
        "/api/v1/permissions/",
        json={"name": "重复权限", "code": "test:permission", "description": "重复编码"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 400

def test_get_permissions(setup_database, admin_token):
    """测试获取权限列表"""
    response = client.get(
        "/api/v1/permissions/",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_permission(setup_database, admin_token):
    """测试获取单个权限"""
    permissions = client.get("/api/v1/permissions/", headers={"Authorization": admin_token}).json()
    if permissions:
        permission_id = permissions[0]["id"]
        response = client.get(
            f"/api/v1/permissions/{permission_id}",
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["id"] == permission_id

def test_get_permission_not_found(setup_database, admin_token):
    """测试获取权限失败-权限不存在"""
    response = client.get(
        "/api/v1/permissions/999",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_update_permission(setup_database, admin_token):
    """测试更新权限"""
    permissions = client.get("/api/v1/permissions/", headers={"Authorization": admin_token}).json()
    if permissions:
        permission_id = permissions[0]["id"]
        perm_code = permissions[0]["code"]
        response = client.put(
            f"/api/v1/permissions/{permission_id}",
            json={"name": "更新权限", "code": perm_code, "description": "更新描述"},
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "更新权限"

def test_update_permission_not_found(setup_database, admin_token):
    """测试更新权限失败-权限不存在"""
    response = client.put(
        "/api/v1/permissions/999",
        json={"name": "更新权限", "code": "test_perm"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_update_permission_duplicate_code(setup_database, admin_token):
    """测试更新权限失败-编码重复"""
    # 创建两个权限
    client.post(
        "/api/v1/permissions/",
        json={"name": "权限1", "code": "perm1", "description": "权限1"},
        headers={"Authorization": admin_token}
    )
    perm2_response = client.post(
        "/api/v1/permissions/",
        json={"name": "权限2", "code": "perm2", "description": "权限2"},
        headers={"Authorization": admin_token}
    )
    perm2_id = perm2_response.json()["id"]
    
    # 尝试将权限2的编码改为权限1的编码
    response = client.put(
        f"/api/v1/permissions/{perm2_id}",
        json={"name": "权限2更新", "code": "perm1", "description": "重复编码"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 400

def test_delete_permission(setup_database, admin_token):
    """测试删除权限"""
    # 创建一个新权限用于删除测试
    perm_response = client.post(
        "/api/v1/permissions/",
        json={"name": "待删除权限", "code": "delete_perm", "description": "待删除"},
        headers={"Authorization": admin_token}
    )
    perm_id = perm_response.json()["id"]
    
    # 删除权限
    delete_response = client.delete(
        f"/api/v1/permissions/{perm_id}",
        headers={"Authorization": admin_token}
    )
    assert delete_response.status_code == 200

def test_delete_permission_not_found(setup_database, admin_token):
    """测试删除权限失败-权限不存在"""
    response = client.delete(
        "/api/v1/permissions/999",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_delete_permission_with_role(setup_database, admin_token):
    """测试删除权限失败-权限已被角色使用"""
    # 创建权限
    perm_response = client.post(
        "/api/v1/permissions/",
        json={"name": "已使用权限", "code": "used_perm", "description": "已分配"},
        headers={"Authorization": admin_token}
    )
    perm_id = perm_response.json()["id"]
    
    # 创建角色并分配权限
    client.post(
        "/api/v1/roles/",
        json={"name": "测试角色2", "code": "test_role2", "permission_ids": [perm_id]},
        headers={"Authorization": admin_token}
    )
    
    # 尝试删除权限
    delete_response = client.delete(
        f"/api/v1/permissions/{perm_id}",
        headers={"Authorization": admin_token}
    )
    assert delete_response.status_code == 400

# ==================== 认证模块测试 ====================

def test_password_hashing():
    """测试密码哈希功能"""
    password = "Test@123"
    hashed = hash_password(password)
    assert hashed is not None
    assert len(hashed) > 0
    # 验证哈希格式（bcrypt格式）
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$") or hashed.startswith("$2y$")

def test_token_creation():
    """测试JWT令牌创建"""
    token = create_access_token(data={"sub": "testuser"})
    assert token is not None
    assert isinstance(token, str)
    # JWT格式验证
    parts = token.split(".")
    assert len(parts) == 3

# ==================== 手机管理测试 ====================

def test_create_phone(setup_database, admin_token):
    """测试创建手机"""
    response = client.post(
        "/api/v1/phones/",
        json={
            "name": "测试手机",
            "brand": "TestBrand",
            "model": "ModelX",
            "price": 1999.99,
            "stock": 100,
            "description": "测试手机描述"
        },
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "测试手机"

def test_get_phones(setup_database, admin_token):
    """测试获取手机列表"""
    response = client.get(
        "/api/v1/phones/",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_phone(setup_database, admin_token):
    """测试获取单个手机"""
    phones = client.get("/api/v1/phones/", headers={"Authorization": admin_token}).json()
    if phones:
        phone_id = phones[0]["id"]
        response = client.get(
            f"/api/v1/phones/{phone_id}",
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["id"] == phone_id

def test_get_phone_not_found(setup_database, admin_token):
    """测试获取手机失败-手机不存在"""
    response = client.get(
        "/api/v1/phones/999",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_update_phone(setup_database, admin_token):
    """测试更新手机"""
    phones = client.get("/api/v1/phones/", headers={"Authorization": admin_token}).json()
    if phones:
        phone_id = phones[0]["id"]
        response = client.put(
            f"/api/v1/phones/{phone_id}",
            json={"name": "更新手机", "price": 2999.99},
            headers={"Authorization": admin_token}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "更新手机"

def test_update_phone_not_found(setup_database, admin_token):
    """测试更新手机失败-手机不存在"""
    response = client.put(
        "/api/v1/phones/999",
        json={"name": "更新手机"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

def test_delete_phone(setup_database, admin_token):
    """测试删除手机"""
    # 创建手机
    phone_response = client.post(
        "/api/v1/phones/",
        json={
            "name": "待删除手机",
            "brand": "Brand",
            "model": "Model",
            "price": 999.99,
            "stock": 10
        },
        headers={"Authorization": admin_token}
    )
    phone_id = phone_response.json()["id"]
    
    # 删除手机
    delete_response = client.delete(
        f"/api/v1/phones/{phone_id}",
        headers={"Authorization": admin_token}
    )
    assert delete_response.status_code == 200

def test_delete_phone_not_found(setup_database, admin_token):
    """测试删除手机失败-手机不存在"""
    response = client.delete(
        "/api/v1/phones/999",
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 404

# ==================== 公共商品测试 ====================

def test_get_public_products():
    """测试获取公共商品列表"""
    response = client.get("/api/v1/public/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_public_products_search():
    """测试搜索公共商品"""
    response = client.get("/api/v1/public/products?search=test")
    assert response.status_code == 200

def test_get_public_products_sort():
    """测试排序公共商品"""
    response = client.get("/api/v1/public/products?sort=price_asc")
    assert response.status_code == 200
    
    response = client.get("/api/v1/public/products?sort=price_desc")
    assert response.status_code == 200
    
    response = client.get("/api/v1/public/products?sort=created_new")
    assert response.status_code == 200
    
    response = client.get("/api/v1/public/products?sort=created_old")
    assert response.status_code == 200

def test_get_public_product_not_found():
    """测试获取公共商品失败-商品不存在"""
    response = client.get("/api/v1/public/products/999")
    assert response.status_code == 404

# ==================== 任务管理扩展测试 ====================

def test_create_task_with_assignee(setup_database, admin_token):
    """测试创建任务（带负责人）"""
    response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "带负责人任务",
            "description": "测试负责人字段",
            "status": "pending",
            "priority": "high",
            "assigned_to": 1
        },
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200

def test_create_task_with_group(setup_database, admin_token):
    """测试创建任务（带组）"""
    # 先创建一个组
    group_response = client.post(
        "/api/v1/groups/",
        json={"name": "任务组", "code": "task_group", "description": "任务测试组"},
        headers={"Authorization": admin_token}
    )
    group_id = group_response.json()["id"]
    
    # 创建带组的任务
    response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "组任务",
            "description": "测试组关联",
            "status": "pending",
            "priority": "medium",
            "group_id": group_id
        },
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 200

def test_get_tasks_filter_type(setup_database, admin_token):
    """测试按类型筛选任务"""
    response = client.get("/api/v1/tasks/?type=all", headers={"Authorization": admin_token})
    assert response.status_code == 200

def test_get_tasks_filter_priority(setup_database, admin_token):
    """测试按优先级筛选任务"""
    response = client.get("/api/v1/tasks/?priority=high", headers={"Authorization": admin_token})
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])