from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.utils.run_workflow import error_check,error_checkv3,succes_summary
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter()
logger = get_logger(__name__)

class ErrorCheckRequest(BaseModel):
    info: Dict[str, Any]

class ErrorCheckResponse(BaseModel):
    code: int
    message: str
    check_result: Optional[Dict[str, Any]] = None

@router.post("/error_checked", response_model=ErrorCheckResponse)
async def error_check_endpoint(request: ErrorCheckRequest):
    """
    错误检查接口
    基于输入信息检查错误
    """
    logger.info(f"收到错误检查请求")
    
    try:
        # 调用错误检查函数
        check_result = await error_check(request.info)
        
        if check_result == -1:
            raise HTTPException(
                status_code=500,
                detail="错误检查失败"
            )
        
        return ErrorCheckResponse(
            code=200,
            message="Success",
            check_result=check_result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"错误检查失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/succes_summary", response_model=ErrorCheckResponse)
async def succes_summary_endpoint(request: ErrorCheckRequest):
    """
    错误检查接口
    基于输入信息检查错误
    """
    logger.info(f"收到错误检查请求")
    
    try:
        # 调用错误检查函数
        check_result = await succes_summary(request.info)
        
        if check_result == -1:
            raise HTTPException(
                status_code=500,
                detail="错误检查失败"
            )
        
        return ErrorCheckResponse(
            code=200,
            message="Success",
            check_result=check_result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"错误检查失败: {e}")
        return ErrorCheckResponse(
            code=400,
            message="请求失败",
            check_result={"error":f"Internal server error: {str(e)}"}
        )

        # raise HTTPException(
        #     status_code=500,
        #     detail=f"Internal server error: {str(e)}"
        # )


@router.post("/error_checkedv3", response_model=ErrorCheckResponse)
async def error_checkv3_endpoint(request: ErrorCheckRequest):
    """
    错误检查接口
    基于输入信息检查错误
    """
    logger.info(f"收到错误检查请求")
    
    try:
        # 调用错误检查函数
        check_result = await error_checkv3(request.info)
        
        if check_result == -1:
            raise HTTPException(
                status_code=500,
                detail="错误检查失败"
            )
        
        return ErrorCheckResponse(
            code=200,
            message="Success",
            check_result=check_result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"错误检查失败: {e}")
        return ErrorCheckResponse(
            code=400,
            message="请求失败",
            check_result={"error":f"Internal server error: {str(e)}"}
        )
        # raise HTTPException(
        #     status_code=500,
        #     detail=f"Internal server error: {str(e)}"
        # )