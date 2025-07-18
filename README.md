# FastAPI 意图识别后端项目

这是一个基于FastAPI构建的模块化后端项目，以意图识别为例展示了完整的项目架构。

## 项目结构

```
app/
├── __init__.py
├── main.py                 # FastAPI主应用
├── api/                    # API层
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── api.py         # API路由聚合
│       └── endpoints/     # API端点
│           ├── __init__.py
│           └── intent.py  # 意图识别端点
├── core/                   # 核心配置
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   └── logging.py         # 日志配置
├── models/                 # 模型层
│   ├── __init__.py
│   └── intent_model.py    # 意图识别模型
├── schemas/                # 数据模型
│   ├── __init__.py
│   └── intent.py          # 意图识别数据模型
├── services/               # 业务逻辑层
│   ├── __init__.py
│   └── intent_service.py  # 意图识别服务
├── utils/                  # 工具类
│   ├── __init__.py
│   ├── text_processor.py  # 文本处理工具
│   └── validators.py      # 数据验证工具
└── middleware/             # 中间件
    ├── __init__.py
    └── logging_middleware.py  # 日志中间件
```

## 功能特性

- **模块化架构**: 清晰的分层结构，便于维护和扩展
- **意图识别**: 支持多种意图类型的识别（天气查询、时间查询、问候等）
- **意图检测**: 专门用于判断查询是否与生物信息学分析相关
- **日志系统**: 完整的日志记录，支持文件和控制台输出
- **数据验证**: 严格的输入数据验证和清理
- **错误处理**: 统一的错误处理和响应格式
- **API文档**: 自动生成的Swagger文档

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件：

```bash
cp env.example .env
```

根据需要修改 `.env` 文件中的配置。

### 3. 运行应用

```bash
python run.py
```

或者使用uvicorn直接运行：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问API文档

启动后访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. 运行测试

```bash
# 运行完整API测试
python test_api.py

# 运行意图检测专项测试
python test_intent_detection.py

# 运行演示脚本
python demo_intent_detection.py
```

## API接口

### 意图识别

#### 单个意图识别

```http
POST /api/v1/intent/recognize
Content-Type: application/json

{
    "text": "我想查询今天的天气",
    "user_id": "user123",
    "session_id": "session456"
}
```

响应示例：

```json
{
    "text": "我想查询今天的天气",
    "intent": "weather_query",
    "confidence": 0.95,
    "all_intents": [
        {"intent": "weather_query", "confidence": 0.95},
        {"intent": "general_query", "confidence": 0.03},
        {"intent": "unknown", "confidence": 0.02}
    ],
    "entities": {
        "time": "今天",
        "query_type": "天气"
    },
    "processing_time": 150.5,
    "timestamp": "2024-01-01T12:00:00"
}
```

#### 获取可用意图列表

```http
GET /api/v1/intent/intents
```

#### 批量意图识别

```http
POST /api/v1/intent/batch
Content-Type: application/json

[
    {"text": "今天天气怎么样"},
    {"text": "你好"},
    {"text": "现在几点了"}
]
```

#### 意图检测（生物信息学相关）

```http
POST /api/v1/intent/intent_detection
Content-Type: application/json

{
    "query": "富集分析"
}
```

响应示例：

```json
{
    "code": 200,
    "message": "Success",
    "intent": 1,
    "is_bioinformatics_related": true
}
```

**意图分类说明：**
- `intent: 1` - 标准生物信息学分析相关
- `intent: 0` - 非生物信息学相关
- `intent: 2` - 高级生物信息学分析相关

## 支持的意图类型

- `weather_query`: 天气查询
- `time_query`: 时间查询
- `greeting`: 问候
- `farewell`: 告别
- `help_request`: 帮助请求
- `general_query`: 一般查询
- `unknown`: 未知意图

## 日志配置

项目使用loguru进行日志管理，支持：

- 控制台彩色输出
- 文件日志轮转
- 不同级别的日志记录
- 结构化日志格式

日志文件默认保存在 `logs/app.log`。

## 开发说明

### 添加新的意图类型

1. 在 `app/services/intent_service.py` 中的 `available_intents` 列表添加新意图
2. 在 `_classify_intent` 方法中添加分类规则
3. 在 `app/models/intent_model.py` 中的 `_rule_based_classification` 方法添加规则

### 添加新的API端点

1. 在 `app/api/v1/endpoints/` 目录下创建新的端点文件
2. 在 `app/api/v1/api.py` 中注册新路由
3. 在 `app/schemas/` 目录下创建相应的数据模型

### 扩展功能

项目采用模块化设计，可以轻松扩展：

- 添加新的服务层处理业务逻辑
- 添加新的模型层处理数据
- 添加新的工具类处理通用功能
- 添加新的中间件处理请求/响应

## 技术栈

- **FastAPI**: 现代、快速的Web框架
- **Pydantic**: 数据验证和序列化
- **Loguru**: 强大的日志库
- **Uvicorn**: ASGI服务器
- **Python 3.8+**: 编程语言

## 许可证

MIT License 