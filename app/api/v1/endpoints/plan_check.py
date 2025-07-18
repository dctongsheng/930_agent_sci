from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.utils.run_workflow import plan_check
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter()
logger = get_logger(__name__)

class PlanCheckRequest(BaseModel):
    plan_desc: Dict[str, Any]

class PlanCheckResponse(BaseModel):
    code: int
    message: str
    check_result: Optional[Dict[str, Any]] = None

@router.post("/plan_check", response_model=PlanCheckResponse)
async def plan_check_endpoint(request: PlanCheckRequest):
    """
    计划检查接口
    基于plan_desc检查计划的有效性
    """
    logger.info(f"收到计划检查请求")
    
    try:
        # 调用计划检查函数
        check_result = await plan_check(request.plan_desc)
        
        if check_result == -1:
            raise HTTPException(
                status_code=500,
                detail="计划检查失败"
            )
        
        return PlanCheckResponse(
            code=200,
            message="Success",
            check_result=check_result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"计划检查失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
