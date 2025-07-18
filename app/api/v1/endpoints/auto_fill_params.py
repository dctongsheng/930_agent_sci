from fastapi import APIRouter, HTTPException, Depends
from app.core.logging import get_logger
from app.schemas.auto_fill_schema import AutoFilledParamsRequest, AutoFilledParamsResponse
from app.utils.call_dify import get_filled_parameters
import json

router = APIRouter()
logger = get_logger(__name__)

@router.get("/test")
async def test(request: AutoFilledParamsRequest):
    logger.info(f"收到意图检测请求: {request.query_template}")
    return {"message": "Hello, World!"}

@router.post("/auto_filled_params", response_model=AutoFilledParamsResponse)
async def auto_fill_parameters_endpoint(request: AutoFilledParamsRequest):
    """
    自动填写参数接口
    基于data_choose和query_template自动填充参数
    """
    # print(f"接收到的data_choose: {request.data_meatinfo}")
    rrr = request.data_meatinfo
    logger.info(f"收到意图检测请求: {request.query_template}")
    res = json.dumps(rrr)
    try:
        # 调用自动填写参数函数
        filled_params = await get_filled_parameters(
            data_choose=res,  # 直接传递，不转换为JSON字符串
            query_template=json.dumps(request.query_template),
            user=request.user,
            conversation_id=request.conversation_id,
            response_mode=request.response_mode
        )
        
        return AutoFilledParamsResponse(
            code=200,
            message="Success",
            filled_parameters=filled_params
        )
    except Exception as e:
        if "API key" in str(e):
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        elif "rate limit" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}")

@router.post("/auto_filled_paramsv2", response_model=AutoFilledParamsResponse)
async def auto_fill_parameters_v2_endpoint(request: AutoFilledParamsRequest):
    """
    自动填写参数接口 v2
    基于main函数的简化版本
    """
    logger.info(f"收到v2请求: {request.query_template}")
    rrr = request.data_meatinfo
    logger.info(f"收到意图检测请求: {request.query_template}")
    res = json.dumps(rrr)
    
    try:
        # 调用自动填写参数函数
        filled_params = await get_filled_parameters(
            data_choose=rrr,
            query_template=str(request.query_template),
            user=request.user,
            conversation_id=request.conversation_id,
            response_mode=request.response_mode
        )
        
        return AutoFilledParamsResponse(
            code=200,
            message="Success",
            filled_parameters=filled_params
        )
    except Exception as e:
        logger.error(f"处理请求时出错: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )