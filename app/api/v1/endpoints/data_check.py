from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.utils.run_workflow import data_check
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter()
logger = get_logger(__name__)

class DataCheckRequest(BaseModel):
    data: Dict[str, Any]

class DataCheckResponse(BaseModel):
    code: int
    message: str
    check_result: Optional[Dict[str, Any]] = None

@router.post("/data_check", response_model=DataCheckResponse)
async def data_check_endpoint(request: DataCheckRequest):
    """
    数据检查接口
    """
    logger.info("收到数据检查请求")
    try:
        check_result = await data_check(request.data)
        if check_result == -1:
            raise HTTPException(status_code=500, detail="数据检查失败")
        return DataCheckResponse(
            code=200,
            message="Success",
            check_result=check_result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"数据检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
