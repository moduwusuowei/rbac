# RBAC System - 基于角色的访问控制系统

一个完整的全栈 RBAC (Role-Based Access Control) 系统，使用 Python FastAPI 后端和 Vue 3 + Element Plus 前端。

## 项目特点

- **后端**: FastAPI + SQLModel + JWT 认证
- **前端**: Vue 3 + Composition API + Element Plus + Pinia
- **数据库**: SQLite (可轻松切换为 PostgreSQL/MySQL)
- **架构**: 三层架构 (API -> Service -> Model)
- **特性**: 
  - JWT Token 认证
  - 基于角色的权限控制 (RBAC)
  - 动态路由权限
  - 响应式布局

## 项目结构

```
rbac-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py          # 认证API
│   │   │       ├── users.py         # 用户管理API
│   │   │       └── roles.py         # 角色管理API
│   │   ├── core/
│   │   │   ├── auth.py             # JWT认证与权限校验
│   │   │   ├── config.py           # 配置管理
│   │   │   ├── database.py         # 数据库连接
│   │   │   └── dependencies.py     # 依赖注入
│   │   ├── models/
│   │   │   └── user_model.py       # 数据库模型
│   │   ├── routers/
│   │   │   └── api_router.py       # 路由注册
│   │   ├── schemas/
│   │   │   └── auth.py             # Pydantic schemas
│   │   └── main.py                 # 应用入口
│   ├── requirements.txt
│   └── rbac.db                     # SQLite数据库(启动后生成)
│
└── frontend/
    ├── src/
    │   ├── api/
    │   │   └── auth.js             # 认证API服务
    │   ├── assets/
    │   │   ├── logo.svg
    │   │   └── main.css
    │   ├── components/
    │   ├── layouts/
    │   │   └── AppLayout.vue       # 应用布局
    │   ├── router/
    │   │   └── index.js            # Vue Router配置
    │   ├── stores/
    │   │   └── user.js             # Pinia用户状态
    │   ├── utils/
    │   │   └── request.js          # Axios封装
    │   ├── views/
    │   │   ├── Dashboard.vue       # 仪表盘
    │   │   ├── Forbidden.vue       # 403页面
    │   │   ├── Login.vue           # 登录页
    │   │   ├── NotFound.vue        # 404页面
    │   │   ├── RoleManagement.vue  # 角色管理
    │   │   └── UserManagement.vue  # 用户管理
    │   ├── App.vue
    │   └── main.js
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## 快速开始

### 1. 环境要求

- Python 3.9+
- Node.js 18+
- npm 或 yarn

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问系统

- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 超级管理员 |
| user | user123 | 普通用户 |

## 核心功能

### 后端

1. **用户管理**: CRUD 用户，分配角色
2. **角色管理**: CRUD 角色，分配权限
3. **认证**: JWT Token 登录
4. **权限**: 基于 Depends 的权限校验

### 前端

1. **登录**: 获取 Token，自动携带
2. **仪表盘**: 展示用户信息
3. **用户管理**: 表格展示，增删改查
4. **角色管理**: 角色权限分配
5. **权限控制**: 路由级别 + 组件级别权限控制

## API 接口

### 认证接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/v1/auth/login | 用户登录 | 公开 |
| GET | /api/v1/auth/me | 获取当前用户 | 需要认证 |

### 用户接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/v1/users | 获取用户列表 | user:read |
| GET | /api/v1/users/{id} | 获取单个用户 | user:read |
| POST | /api/v1/users | 创建用户 | user:create |
| PUT | /api/v1/users/{id} | 更新用户 | user:update |
| DELETE | /api/v1/users/{id} | 删除用户 | user:delete |

### 角色接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/v1/roles | 获取角色列表 | role:read |
| GET | /api/v1/roles/{id} | 获取单个角色 | role:read |
| POST | /api/v1/roles | 创建角色 | role:manage |
| PUT | /api/v1/roles/{id} | 更新角色 | role:manage |
| DELETE | /api/v1/roles/{id} | 删除角色 | role:manage |

## 权限设计

### 权限列表

- `user:read`: 查看用户
- `user:create`: 创建用户
- `user:update`: 编辑用户
- `user:delete`: 删除用户
- `role:read`: 查看角色
- `role:manage`: 管理角色

### 角色

- **超级管理员 (admin)**: 拥有所有权限
- **普通用户 (user)**: 仅 `user:read` 权限

## 技术栈

### 后端

- **FastAPI**: 现代 Python Web 框架
- **SQLModel**: SQLAlchemy + Pydantic
- **JWT**: JSON Web Token 认证
- **Passlib**: 密码加密

### 前端

- **Vue 3**: 渐进式 JavaScript 框架
- **Vite**: 下一代前端构建工具
- **Element Plus**: Vue 3 UI 组件库
- **Pinia**: Vue 状态管理
- **Vue Router**: Vue 路由管理
- **Axios**: HTTP 客户端

## 扩展建议

1. **数据库切换**: 修改 `DATABASE_URL` 配置
2. **更多权限**: 在 `Permission` 模型中添加
3. **审计日志**: 添加用户操作日志
4. **缓存**: 集成 Redis 缓存
5. **分页**: 实现列表分页功能

## 许可证

MIT License"# rbac" 
