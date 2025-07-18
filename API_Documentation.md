# API 文档

## 自动填写参数接口

### 1. 自动填写参数 v1
- **路由**: `POST /auto_filled_params`
- **功能**: 基于数据选择自动填充参数模板
- **请求**:
  ```json
  {
    "data_meatinfo": {"your": "data"},
    "query_template": {"SN": "", "RegistJson": ""},
    "user": "abc-123",
    "conversation_id": "",
    "response_mode": "blocking"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "Success",
    "filled_parameters": {"SN": "value", "RegistJson": "value"}
  }
  ```

### 2. 自动填写参数 v2
- **路由**: `POST /auto_filled_paramsv2`
- **功能**: 简化版本的自动填写参数接口
- **请求**: 同v1
- **响应**: 同v1

## 规划生成接口

### 3. 规划生成
- **路由**: `POST /planning_generate`
- **功能**: 基于数据和查询生成分析规划
- **请求**:
  ```json
  {
    "data_meatinfo": {"your": "data"},
    "query": "富集分析"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "Success",
    "planning_result": {
      "structured_output": {
        "planning_steps": ["step1", "step2"]
      }
    }
  }
  ```

## 计划检查接口

### 4. 计划检查
- **路由**: `POST /plan_check`
- **功能**: 检查计划的有效性和可行性
- **请求**:
  ```json
  {
    "plan_desc": {"plan": "description"}
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "Success",
    "check_result": {"check": "result"}
  }
  ```

## 测试接口

### 5. 测试接口
- **路由**: `GET /test`
- **功能**: 简单的测试接口
- **响应**: `{"message": "Hello, World!"}` 