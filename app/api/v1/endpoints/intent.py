from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.services.intent_service import IntentService
from app.core.logging import get_logger
from app.schemas.intent import IntentRequest, IntentResponse, IntentConfidence, IntentDetectionRequest, IntentDetectionResponse
from app.utils.run_workflow import intent_detection

router = APIRouter()
logger = get_logger(__name__)

# 依赖注入
def get_intent_service():
    """获取意图识别服务实例"""
    return IntentService()

@router.post("/recognize", response_model=IntentResponse)
async def recognize_intent(
    request: IntentRequest,
    intent_service: IntentService = Depends(get_intent_service)
):
    """
    意图识别接口
    
    Args:
        request: 包含用户输入的请求
        intent_service: 意图识别服务
        
    Returns:
        IntentResponse: 识别结果
    """
    try:
        logger.info(f"收到意图识别请求: {request.text}")
        
        # 调用意图识别服务
        result = await intent_service.recognize_intent(request.text)
        
        logger.info(f"意图识别完成: {result.intent}, 置信度: {result.confidence}")
        
        return result
        
    except Exception as e:
        logger.error(f"意图识别失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"意图识别失败: {str(e)}")

@router.get("/intents", response_model=List[str])
async def get_available_intents(
    intent_service: IntentService = Depends(get_intent_service)
):
    """
    获取所有可用的意图类型
    
    Returns:
        List[str]: 意图类型列表
    """
    try:
        intents = await intent_service.get_available_intents()
        logger.info(f"获取可用意图列表: {len(intents)} 个")
        return intents
    except Exception as e:
        logger.error(f"获取意图列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取意图列表失败: {str(e)}")

@router.post("/batch", response_model=List[IntentResponse])
async def batch_recognize_intent(
    requests: List[IntentRequest],
    intent_service: IntentService = Depends(get_intent_service)
):
    """
    批量意图识别接口
    
    Args:
        requests: 包含多个用户输入的请求列表
        intent_service: 意图识别服务
        
    Returns:
        List[IntentResponse]: 识别结果列表
    """
    try:
        logger.info(f"收到批量意图识别请求: {len(requests)} 条")
        
        results = []
        for request in requests:
            result = await intent_service.recognize_intent(request.text)
            results.append(result)
        
        logger.info(f"批量意图识别完成: {len(results)} 条")
        return results
        
    except Exception as e:
        logger.error(f"批量意图识别失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量意图识别失败: {str(e)}")

@router.post("/intent_detection", response_model=IntentDetectionResponse)
async def detect_intent(request: IntentDetectionRequest):
    """
    意图识别接口
    判断用户查询是否与生物信息学分析相关
    """
    print(request.query)
    try:
        logger.info(f"收到意图检测请求: {request.query}")
        
        # 调用意图识别函数
        intent_result = await intent_detection(request.query)
        
        logger.info(f"意图检测完成: {intent_result}")
        
        return IntentDetectionResponse(
            code=200,
            message="Success",
            intent=intent_result,
            is_bioinformatics_related=intent_result == 1
        )
    except Exception as e:
        logger.error(f"意图检测失败: {str(e)}")
        
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
                detail=f"Internal server error: {str(e)}"
            ) 