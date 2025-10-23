# memoryme 智能代理后端项目

这是一个基于FastAPI构建的智能代理后端项目，专注于生物信息学分析流程的自动化和智能对话。

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
│           ├── multi_chat.py          # 多轮对话接口
│           ├── auto_fill_params.py    # 参数自动填写接口
│           ├── error_checked.py       # 错误检查接口
│           └── query_gpaph_api.py     # 工具替换接口
├── core/                   # 核心配置
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   └── logging.py         # 日志配置
├── models/                 # 模型层
│   ├── __init__.py
│   └── intent_model.py    # 意图识别模型
├── schemas/                # 数据模型
│   ├── __init__.py
│   ├── intent.py          # 意图识别数据模型
│   └── auto_fill_schema.py # 参数自动填写数据模型
├── services/               # 业务逻辑层
│   ├── __init__.py
│   └── intent_service.py  # 意图识别服务
├── utils/                  # 工具类
│   ├── __init__.py
│   ├── call_dify.py       # Dify API调用
│   ├── get_params_v2.py   # 参数获取工具
│   ├── get_params_v3.py   # 参数获取工具v3
│   ├── run_workflow.py    # 工作流运行工具
│   ├── query_graph.py     # 图查询工具
│   ├── replace_tools.py   # 工具替换工具
│   ├── text_processor.py  # 文本处理工具
│   └── validators.py      # 数据验证工具
└── middleware/             # 中间件
    ├── __init__.py
    └── logging_middleware.py  # 日志中间件
```

## 功能特性

- **智能对话**: 支持多轮在线对话，理解用户意图
- **参数自动填写**: 基于用户输入自动填充分析参数
- **错误检查**: 智能检测和总结运行错误
- **成功总结**: 分析运行成功的结果
- **工具替换**: 动态替换和优化分析工具
- **日志系统**: 完整的日志记录，支持文件和控制台输出
- **数据验证**: 严格的输入数据验证和清理
- **错误处理**: 统一的错误处理和响应格式
- **API文档**: 自动生成的Swagger文档

## 安装和运行

### 1. 安装依赖

使用uv包管理器安装依赖：

```bash
uv sync
```

或者使用pip安装：

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

使用uv运行应用：

```bash
uv run run.py
```

或者使用uvicorn直接运行：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10103 --reload
```

### 4. 访问API文档

启动后访问以下地址查看API文档：

- Swagger UI: http://10.224.28.80:10103/docs
- ReDoc: http://10.224.28.80:10103/redoc

### 5. 运行测试

```bash
# 运行完整API测试
python test_api.py

# 运行参数自动填写测试
python test_auto_fill_params.py

# 运行意图检测专项测试
python test_intent_detection.py
```

## API接口

### 1. 对话接口

#### 多轮对话代理

```http
POST /api/v1/multi_chat/multi_chat_agent_prd
Content-Type: application/json

{
    "data_choose": {
        "project_id": "project123",
        "data_info": {...}
    },
    "query_template": "我想进行富集分析",
    "conversation_id": "conv_456",
    "xtoken": "your_token_here",
    "state": 1
}
```

响应示例：

```json
{
    "code": 200,
    "message": "Success",
    "planning_result": {
        "mul_chat": true,
        "text": "我理解您想进行富集分析...",
        "conversation_id": "conv_456",
        "planning_steps": [...]
    }
}
```

### 2. 参数自动填写接口

#### 全计划参数自动填写

```http
POST /api/v1/auto_fill_params/auto_filled_params_all_plan_v3
Content-Type: application/json

{
    "plan_result": {
        "workflow_id": "wf_789",
        "parameters": {...}
    },
    "json_template": {
        "template_id": "tpl_001",
        "fields": [...]
    },
    "xtoken": "your_token_here",
    "user": "abc-123",
    "conversation_id": "conv_456",
    "response_mode": "blocking"
}
```

响应示例：

```json
{
    "code": 200,
    "message": "Success",
    "filled_parameters": {
        "parameter1": "value1",
        "parameter2": "value2",
        "filled_count": 15
    }
}
```

### 3. 运行错误总结接口

#### 错误检查v3

```http
POST /api/v1/error_checked/error_checkedv3
Content-Type: application/json

{
    "info": {
        "workflow_id": "wf_789",
        "error_logs": [...],
        "execution_context": {...}
    }
}
```

响应示例：

```json
{
    "code": 200,
    "message": "Success",
    "check_result": {
        "error_summary": "参数配置错误",
        "error_details": [...],
        "suggestions": [...],
        "severity": "high"
    }
}
```

### 4. 运行成功总结接口

#### 成功总结

```http
POST /api/v1/error_checked/succes_summary
Content-Type: application/json

{
    "info": {
        "workflow_id": "wf_789",
        "execution_logs": [...],
        "results": {...}
    }
}
```

响应示例：

```json
{
    "code": 200,
    "message": "Success",
    "check_result": {
        "success_summary": "分析成功完成",
        "result_summary": {...},
        "performance_metrics": {...}
    }
}
```

### 5. 替换工具接口

#### 工具替换

```http
POST /api/v1/query_gpaph_api/reolace_tools
Content-Type: application/json

{
    "workflow_id": "wf_789"
}
```

响应示例：

```json
{
    "code": 200,
    "message": "Success",
    "result": {
        "alternative_tools": [...],
        "replacement_suggestions": [...],
        "compatibility_matrix": {...}
    }
}
```

## 技术栈

- **FastAPI**: 现代、快速的Web框架
- **Pydantic**: 数据验证和序列化
- **Loguru**: 强大的日志库
- **Uvicorn**: ASGI服务器
- **Neo4j**: 图数据库
- **Pandas**: 数据处理库
- **OpenPyXL**: Excel文件处理
- **Python 3.13+**: 编程语言
- **uv**: 现代Python包管理器

## 日志配置

项目使用loguru进行日志管理，支持：

- 控制台彩色输出
- 文件日志轮转
- 不同级别的日志记录
- 结构化日志格式

日志配置位于 `app/core/logging.py`，日志文件默认保存在 `logs/app.log`。

### 日志级别

- `DEBUG`: 调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

## 开发说明

### 添加新的API端点

1. 在 `app/api/v1/endpoints/` 目录下创建新的端点文件
2. 在 `app/api/v1/api.py` 中注册新路由
3. 在 `app/schemas/` 目录下创建相应的数据模型
4. 在 `app/utils/` 目录下添加业务逻辑处理函数

### 扩展功能

项目采用模块化设计，可以轻松扩展：

- 添加新的服务层处理业务逻辑
- 添加新的模型层处理数据
- 添加新的工具类处理通用功能
- 添加新的中间件处理请求/响应

### 环境配置

项目支持通过环境变量进行配置：

- `PROJECT_NAME`: 项目名称
- `HOST`: 服务器主机地址
- `PORT`: 服务器端口
- `LOG_LEVEL`: 日志级别
- `DEBUG`: 调试模式

## 维护和部署

### 开发环境

```bash
# 安装依赖
uv sync

# 运行开发服务器
uv run run.py
```

### 生产环境

```bash
# 使用uvicorn直接运行
uvicorn app.main:app --host 0.0.0.0 --port 10103 --workers 4
```

## 许可证

MIT License 