from fastapi import APIRouter
from app.api.v1.endpoints import intent
from app.api.v1.endpoints import auto_fill_params
from app.api.v1.endpoints import planning_generate
from app.api.v1.endpoints import plan_check

api_router = APIRouter()

# 注册意图识别路由
api_router.include_router(intent.router, prefix="/intent", tags=["意图识别"]) 
api_router.include_router(auto_fill_params.router, prefix="/auto_fill_params", tags=["自动填写参数"])
api_router.include_router(planning_generate.router, prefix="/planning_generate", tags=["规划生成"])
api_router.include_router(plan_check.router, prefix="/plan_check", tags=["规划检查"])