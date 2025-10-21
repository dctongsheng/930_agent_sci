from fastapi import APIRouter, HTTPException, Depends
from app.core.logging import get_logger
from app.schemas.auto_fill_schema import AutoFilledParamsRequest, AutoFilledParamsResponse,AutoFilledParamsRequestv3
from app.utils.call_dify import get_filled_parameters
from app.utils.get_params_v2 import main_request,main_request_v3
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

@router.post("/auto_filled_params_all_plan", response_model=AutoFilledParamsResponse)
async def auto_fill_parameters_all_plan_endpoint(request: AutoFilledParamsRequest):
    """
    自动填写参数接口 - 全计划版本
    基于get_params_v2.py中main函数的逻辑
    """
    logger.info(f"收到全计划参数填写请求")
    logger.info(request.data_meatinfo)
    # print(request.data_meatinfo)
    
    try:
        # 调用main_request函数处理全计划参数填写    
        result = await main_request(arg1=request.data_meatinfo,file_path=request.query_template)

        print("result:",result)
        logger.info("result:")
        logger.info(result)
        
        return AutoFilledParamsResponse(
            code=200,
            message="Success",
            filled_parameters=result
        )
    except Exception as e:
        logger.error(f"全计划参数填写失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/auto_filled_params_all_plan_v3", response_model=AutoFilledParamsResponse)
async def auto_fill_parameters_all_plan_endpoint_ve(request: AutoFilledParamsRequestv3):
    """
    自动填写参数接口 - 全计划版本
    基于get_params_v2.py中main函数的逻辑
    """
    logger.info(f"收到全计划参数填写请求")
    # logger.info(request.data_meatinfo)
    # print(request.data_meatinfo)
    try:
        # 调用main_request函数处理全计划参数填写    
        result = await main_request_v3(arg1=request.plan_result,file_path=request.json_template)
        print("result:",result)
        logger.info("result:")
        logger.info(result)
        
        return AutoFilledParamsResponse(
            code=200,
            message="Success",
            filled_parameters=result
        )
    except Exception as e:
        logger.error(f"全计划参数填写失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )