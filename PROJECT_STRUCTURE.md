# 项目结构说明

## 整体架构

```
fastapi-intent-recognition/
├── app/                          # 主应用目录
│   ├── __init__.py
│   ├── main.py                   # FastAPI主应用入口
│   ├── api/                      # API层 - 处理HTTP请求
│   │   ├── __init__.py
│   │   └── v1/                   # API版本1
│   │       ├── __init__.py
│   │       ├── api.py            # 路由聚合
│   │       └── endpoints/        # API端点
│   │           ├── __init__.py
│   │           └── intent.py     # 意图识别端点
│   ├── core/                     # 核心配置层
│   │   ├── __init__.py
│   │   ├── config.py             # 配置管理
│   │   └── logging.py            # 日志配置
│   ├── models/                   # 模型层 - 数据模型和AI模型
│   │   ├── __init__.py
│   │   └── intent_model.py       # 意图识别模型
│   ├── schemas/                  # 数据模式层 - Pydantic模型
│   │   ├── __init__.py
│   │   └── intent.py             # 意图识别数据模型
│   ├── services/                 # 业务逻辑层
│   │   ├── __init__.py
│   │   └── intent_service.py     # 意图识别服务
│   ├── utils/                    # 工具类层
│   │   ├── __init__.py
│   │   ├── text_processor.py     # 文本处理工具
│   │   └── validators.py         # 数据验证工具
│   └── middleware/               # 中间件层
│       ├── __init__.py
│       └── logging_middleware.py # 日志中间件
├── logs/                         # 日志文件目录
├── models/                       # 模型文件目录
├── requirements.txt              # Python依赖
├── run.py                       # 应用启动脚本
├── test_api.py                  # API测试脚本
├── start.sh                     # 项目启动脚本
├── env.example                  # 环境变量示例
├── README.md                    # 项目说明文档
└── PROJECT_STRUCTURE.md         # 项目结构说明
```

## 分层架构说明

### 1. API层 (api/)
- **职责**: 处理HTTP请求和响应
- **组件**:
  - `api.py`: 路由聚合，注册所有API端点
  - `endpoints/intent.py`: 意图识别相关的API端点
- **特点**: 只负责请求验证、响应格式化，不包含业务逻辑

### 2. 核心配置层 (core/)
- **职责**: 应用配置和基础设施
- **组件**:
  - `config.py`: 配置管理，使用Pydantic Settings
  - `logging.py`: 日志系统配置，使用Loguru
- **特点**: 提供全局配置和基础设施服务

### 3. 数据模式层 (schemas/)
- **职责**: 定义API请求和响应的数据结构
- **组件**:
  - `intent.py`: 意图识别相关的Pydantic模型
- **特点**: 使用Pydantic进行数据验证和序列化

### 4. 业务逻辑层 (services/)
- **职责**: 实现具体的业务逻辑
- **组件**:
  - `intent_service.py`: 意图识别的业务逻辑
- **特点**: 包含核心业务逻辑，调用模型层和工具类

### 5. 模型层 (models/)
- **职责**: 数据模型和AI模型
- **组件**:
  - `intent_model.py`: 意图识别模型（包含伪代码实现）
- **特点**: 封装模型加载、预测等操作

### 6. 工具类层 (utils/)
- **职责**: 提供通用工具和辅助功能
- **组件**:
  - `text_processor.py`: 文本处理工具
  - `validators.py`: 数据验证工具
- **特点**: 可复用的工具函数

### 7. 中间件层 (middleware/)
- **职责**: 处理请求/响应的横切关注点
- **组件**:
  - `logging_middleware.py`: 请求日志记录
- **特点**: 处理跨切面关注点，如日志、认证等

## 设计原则

### 1. 单一职责原则
- 每个模块只负责一个特定的功能
- 例如：`text_processor.py` 只负责文本处理

### 2. 依赖注入
- 使用FastAPI的依赖注入系统
- 便于测试和模块解耦

### 3. 分层架构
- 清晰的层次结构，上层依赖下层
- 避免跨层依赖

### 4. 配置外部化
- 使用环境变量和配置文件
- 便于部署和环境切换

### 5. 错误处理
- 统一的错误处理机制
- 详细的日志记录

## 扩展指南

### 添加新的API端点
1. 在 `app/api/v1/endpoints/` 创建新的端点文件
2. 在 `app/api/v1/api.py` 中注册路由
3. 在 `app/schemas/` 中定义数据模型

### 添加新的业务逻辑
1. 在 `app/services/` 中创建新的服务类
2. 在 `app/models/` 中创建相关的模型类
3. 在API端点中调用服务

### 添加新的工具类
1. 在 `app/utils/` 中创建新的工具类
2. 在需要的地方导入使用

### 添加新的中间件
1. 在 `app/middleware/` 中创建新的中间件
2. 在 `app/main.py` 中注册中间件

## 文件命名规范

- 文件名使用小写字母和下划线
- 类名使用大驼峰命名法
- 函数和变量使用小写字母和下划线
- 常量使用大写字母和下划线

## 导入规范

- 使用绝对导入，避免相对导入
- 按标准库、第三方库、本地模块的顺序导入
- 每个导入组之间用空行分隔 