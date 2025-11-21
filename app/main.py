from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.middleware.logging_middleware import LoggingMiddleware

# 设置日志
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="基于FastAPI的模块化后端项目 - SciAgent API",
    root_path="/siflow/cks/ai-infra/wsbi/fastapihouduan/wsbidata/10103"
)

# 添加日志中间件
app.add_middleware(LoggingMiddleware)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """根路径"""
    return {"message": "欢迎使用SCIAGENT API", "version": settings.VERSION}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"} 
